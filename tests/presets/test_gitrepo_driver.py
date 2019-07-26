from aiounittest import AsyncTestCase, futurized
from tests.common import example_config
from unittest import mock
from unittest.mock import Mock, patch
from vmshepherd.presets import gitrepo_driver

class MockItem:

    def __init__(self, path):
        self.path = path


class TestGitRepo(AsyncTestCase):

    def setUp(self):
        self.mock_runtime = Mock()
        self.patch_os = patch('vmshepherd.presets.gitrepo_driver.os')
        self.mock_os = self.patch_os.start()

        self.mock_process = Mock()
        self.mock_process.communicate.return_value = futurized(('STDOUT', 'STDERR'))
        self.mock_process.returncode = 0
        self.mock_subprocess_exec = patch(
            'vmshepherd.presets.gitrepo_driver.asyncio.create_subprocess_exec',
            return_value=futurized(self.mock_process)
        ).start()
        self.patch_tmp = patch('vmshepherd.presets.gitrepo_driver.tempfile.TemporaryDirectory')
        self.mock_tmp = self.patch_tmp.start()
        self.mock_tmp.return_value.name = '/tmp/prefixRANDOM_HASH/'

        self.config = {
            'repositories': {
                'paas': 'git://testrepm/paas.git',
                'db': 'git://stash/db.git',
            },
            'clone_dir': '/tmp/'
        }
        self.driver = gitrepo_driver.GitRepoDriver(self.config, self.mock_runtime, example_config['defaults'])

    def tearDown(self):
        patch.stopall()

    def test_init(self):
        self.assertEqual('/tmp/', self.driver._clone_dir)
        self.assertEqual(None, self.driver._presets)

    async def test_clone(self):
        self.mock_os.path.exists.return_value = False

        await self.driver._clone_or_update('/tmp', 'blah')

        self.mock_process.communicate.assert_called_once_with()
        self.mock_subprocess_exec.assert_called_once_with('git', 'clone', 'blah', '/tmp', stderr=-1, stdout=-1)

    async def test_update(self):
        self.mock_os.path.exists.return_value = True

        await self.driver._clone_or_update('/tmp', 'blah')

        self.mock_process.communicate.assert_called_once_with()
        self.mock_subprocess_exec.assert_called_once_with('git', '-C', '/tmp', 'pull', stderr=-1, stdout=-1)

    async def test_update_fail(self):
        self.mock_os.path.exists.return_value = True
        self.mock_process.returncode = 1

        with self.assertRaises(RuntimeError):
            await self.driver._clone_or_update('/tmp', 'blah')

        self.mock_process.communicate.assert_called_once_with()
        self.mock_subprocess_exec.assert_called_once_with('git', '-C', '/tmp', 'pull', stderr=-1, stdout=-1)

    async def test_load_repos_presets(self):
        self.patch_os.stop()
        res = await self.driver._load_repo('blah', example_config['presets']['path'])
        self.assertEqual(res['blah.test-preset']['count'], 1)
        self.assertEqual(res['blah.test-preset']['name'], 'blah.test-preset')
        self.assertEqual(res['blah.test-preset']['flavor'], 'm1.small')
        self.assertEqual(res['blah.test-preset']['image'], 'fedora-27')
        self.assertEqual(res['blah.test-preset']['meta_tags'], {'key1': 'value1'})

    async def test_reload(self):
        self.mock_os.path.join.side_effect = lambda a, b: (a + b)
        self.driver._clone_or_update = Mock(return_value=futurized(None))
        self.driver._assure_clone_dir_exists = Mock(return_value=True)
        self.driver._load_repo = Mock(return_value=futurized({}))
        await self.driver.list_presets()
        self.driver._load_repo.assert_has_calls([
            mock.call('paas', '/tmp/paas'), mock.call('db', '/tmp/db')
        ])
        self.assertEqual(self.driver._load_repo.call_count, 2)

    async def test_reload_tmp_path(self):
        self.mock_os.path.exists.return_value = False
        cfg = {
            'repositories': {
                'paas': 'git://testrepm/paas.git',
                'db': 'git://stash/db.git',
            }}
        driver = gitrepo_driver.GitRepoDriver(cfg, self.mock_runtime, example_config['defaults'])
        self.mock_os.path.join.side_effect = lambda a, b: (a + b)
        driver._clone_or_update = Mock(return_value=futurized(None))
        driver._assure_clone_dir_exists = Mock(return_value=True)
        driver._load_repo = Mock(return_value=futurized({}))
        await driver.list_presets()
        driver._load_repo.assert_has_calls([
            mock.call('paas', '/tmp/prefixRANDOM_HASH/paas'), mock.call('db', '/tmp/prefixRANDOM_HASH/db')
        ])
        self.assertEqual(driver._load_repo.call_count, 2)
