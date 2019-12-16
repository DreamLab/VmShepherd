import asyncio
import errno
import logging
import os
import tempfile
from .abstract import AbstractConfigurationDriver
from asyncio.subprocess import PIPE
from vmshepherd.utils import async_load_from_yaml_file


class GitRepoDriver(AbstractConfigurationDriver):

    def __init__(self, config, runtime, defaults):
        super().__init__(runtime, defaults)
        self._clone_dir = config.get('clone_dir', tempfile.TemporaryDirectory(prefix='vmshepherd').name)
        self._repos = config['repositories']
        self._specs = {}
        self.lock = asyncio.Lock()

    async def _get_preset_spec(self, preset_name: str):
        return self._specs[preset_name]

    async def _list(self):
        await self.reload()
        return self._specs.keys()

    async def reload(self):
        _tmp_specs = {}
        self._assure_clone_dir_exists()
        for name, repo in self._repos.items():
            try:
                path = os.path.join(self._clone_dir, name)
                await self._clone_or_update(path, repo)
                added = await self._load_repo(name, path)
                _tmp_specs.update(added)
            except Exception:
                logging.exception('GitReposDriver: Could not load %s from %s', name, repo)
        self._specs = _tmp_specs

    async def _load_repo(self, repo_name, path):
        loaded = {}
        for item in os.scandir(path):
            if os.path.isfile(item.path) and os.path.splitext(item.path)[1] == '.conf':
                config = await async_load_from_yaml_file(item.path)
                # prepend repo name to preset_name
                config['name'] = preset_name = f"{repo_name}.{config['name']}"
                config['userdata_source_root'] = path
                if 'meta_tags' not in config:
                    config['meta_tags'] = {}
                loaded[preset_name] = config
        return loaded

    async def _clone_or_update(self, path, repo):
        try:
            await self.lock.acquire()
            if os.path.exists(path):
                cmd = ['git', '-C', path, 'pull']
            else:
                cmd = ['git', 'clone', repo, path]
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=PIPE, stderr=PIPE
            )
            stdout, stderr = await process.communicate()
            logging.debug('GitRepo code=%s stdout: %s stderr: %s', process.returncode, stdout, stderr)
            if process.returncode != 0:
                logging.error('Git error: %s %s %s', path, repo, stderr)
                raise RuntimeError(f'Could not fetch presets ({path}) from {repo}')
        finally:
            self.lock.release()

    def _assure_clone_dir_exists(self):
        try:
            os.makedirs(self._clone_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def reconfigure(self, config, defaults):
        super().reconfigure(config, defaults)
        self._clone_dir = config.get('clone_dir', self._clone_dir)
        self._repos = config.get('repositories', self._repos)
