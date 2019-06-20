import unittest
import unittest.mock
import os
from pathlib import Path
from lassh import lassh
from click.testing import CliRunner


class TestLasshFile(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()
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
