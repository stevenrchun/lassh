import unittest
import unittest.mock
import os
from pathlib import Path
from lassh import lassh
from sshconf import read_ssh_config
from click.testing import CliRunner


class TestLasshFile(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def __init_lassh_config(self):
        print('sec')

    # mock pathlib's expanduser to use the temp directory
    @unittest.mock.patch('lassh.HOME_SSH_DIR_PATH', Path("./.ssh"))
    @unittest.mock.patch('lassh.HOME_SSH_CONFIG_PATH', Path("./.ssh/config"))
    def test_init(self):
        with self.runner.isolated_filesystem():
            self.runner.invoke(lassh, ['init'])
            with open("./.ssh/config", 'r+') as config:
                file_contents = config.read()
            # assert that the include was properly generated
            expected_contents = 'Include {0}/lassh.config\n'.format(
                os.getcwd())
            self.assertEqual(file_contents, expected_contents)

    """
    read lassh.config file, iterate backwards until you get to the first line
    starting with Host(space)
    then compare with expected string
    """

    @unittest.mock.patch('lassh.HOME_SSH_DIR_PATH', Path("./.ssh"))
    @unittest.mock.patch('lassh.HOME_SSH_CONFIG_PATH', Path("./.ssh/config"))
    @unittest.mock.patch('lassh.HOME_LASSH_DIR_PATH', Path("./.lassh"))
    @unittest.mock.patch(
        'lassh.HOME_LASSH_NAMESPACE_PATH', Path("./.lassh/namespace"))
    def test_addhost(self):
        # create lassh.config
        with self.runner.isolated_filesystem():
            self.runner.invoke(lassh, ['init'])

            self.runner.invoke(
                lassh, ['addhost', 'snafu', 'foobar@dartmouth.edu', 'sally'])

            with open("./lassh.config", 'r+') as config:
                config_contents = config.read()

            expected_contents = (
                '\nHost snafu\n  HostName foobar@dartmouth.edu\n  User sally\n'
            )

        self.assertEqual(config_contents, expected_contents)

    # TODO:
    # test deletehost, where it exists and it doesn't
    @unittest.mock.patch('lassh.HOME_SSH_DIR_PATH', Path("./.ssh"))
    @unittest.mock.patch('lassh.HOME_SSH_CONFIG_PATH', Path("./.ssh/config"))
    @unittest.mock.patch('lassh.HOME_LASSH_DIR_PATH', Path("./.lassh"))
    @unittest.mock.patch(
        'lassh.HOME_LASSH_NAMESPACE_PATH', Path("./.lassh/namespace"))
    def test_deletehost(self):

        with self.runner.isolated_filesystem():
            self.runner.invoke(lassh, ['init'])

            self.runner.invoke(
                lassh, ['addhost', 'snafu', 'foobar@dartmouth.edu', 'henry'])

            config = read_ssh_config(Path("./lassh.config").resolve())
            self.assertEqual(len(config.hosts()), 1)

            # Now, delete newly added host
            self.runner.invoke(
                lassh, ['deletehost', 'snafu']
            )

            config = read_ssh_config(Path("./lassh.config").resolve())
            self.assertEqual(len(config.hosts()), 0)

            # test removal when hostname doesn't exist
            self.runner.invoke(
                lassh, ['deletehost', 'snafu']
            )
            self.assertEqual(len(config.hosts()), 0)

    # test duplicates
    # In testing teardown,
    # test removal of nickname from global namespace
    # test deletion of lassh.config file
