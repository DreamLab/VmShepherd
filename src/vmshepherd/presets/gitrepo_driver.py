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
        self._presets = {}
        self._clone_dir = config.get('clone_dir', os.path.join(tempfile.gettempdir(), 'vmshepherd'))
        self._repos = config['repositories']

    async def get(self, preset_name):
        return self._presets[preset_name]

    async def get_presets_list(self):
        return list(self._presets.keys())

    async def reload(self):
        presets = {}
        self._assure_clone_dir_exists()
        for name, repo in self._repos.items():
            try:
                path = os.path.join(self._clone_dir, name)
                await self._clone_or_update(path, repo)
                repo_presets = await self._load_repos_presets(name, path)
                presets.update(repo_presets)
            except Exception:
                logging.exception('GitReposDriver: Could not load %s from %s', name, repo)
        self._presets = presets

    async def _load_repos_presets(self, repo_name, path):
        loaded = {}
        for item in os.scandir(path):
            if os.path.isfile(item.path) and os.path.splitext(item.path)[1] == '.conf':
                preset = await async_load_from_yaml_file(item.path)
                # prepend repo name to preset_name
                preset['name'] = preset_name = f"{repo_name}.{preset['name']}"
                if preset is not None:
                    await self.inject_preset_userdata(preset, path)
                    loaded[preset_name] = self.create_preset(preset)
        return loaded

    async def _clone_or_update(self, path, repo):
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