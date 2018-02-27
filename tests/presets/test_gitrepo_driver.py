from unittest.mock import Mock, patch
from aiounittest import AsyncTestCase, futurized
from vmshepherd.presets import gitrepo_driver


class MockItem:

    def __init__(self, path):
        self.path = path


class TestGitRepo(AsyncTestCase):

    def setUp(self):
        self.mock_runtime = Mock()
        self.mock_os = patch(
            'vmshepherd.presets.gitrepo_driver.os'
        ).start()

        self.mock_process = Mock()
        self.mock_process.communicate.return_value = futurized(('STDOUT', 'STDERR'))
        self.mock_process.returncode = 0
        self.mock_subprocess_exec = patch(
            'vmshepherd.presets.gitrepo_driver.asyncio.create_subprocess_exec',
            return_value=futurized(self.mock_process)
        ).start()

        self.config = {
            'repositories': {
                r'paas': 'git://testrepm/paas.git',
                'db': 'git://stash/db.git',
            },
            'clone_dir': '/tmp/'
        }
        self.driver = gitrepo_driver.GitRepoDriver(self.config, self.mock_runtime, {})

    def tearDown(self):
        patch.stopall()

    def test_init(self):
        self.assertEqual('/tmp/', self.driver._clone_dir)
        self.assertEqual({}, self.driver._presets)

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

        with self.assertRaises(RuntimeError) as e:
            await self.driver._clone_or_update('/tmp', 'blah')

        self.mock_process.communicate.assert_called_once_with()
        self.mock_subprocess_exec.assert_called_once_with('git', '-C', '/tmp', 'pull', stderr=-1, stdout=-1)


    async def test_load_repos_presets(self):
        self.driver.create_preset = Mock()
        self.mock_os.path.isfile.return_value = True
        self.mock_os.path.scandir.return_value = [MockItem('A_lala'), MockItem('R_wawa')]
        await self.driver._load_repos_presets('blah', 'git://repo.git')
