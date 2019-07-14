"""
Module implements functionality for creating ssh configs programatically
"""
from pathlib import Path
import os
from clint.textui import puts, colored
from sshconf import read_ssh_config
import click

__version__ = "0.1.0"

HOME_SSH_CONFIG_PATH = Path("~/.ssh/config").expanduser()
HOME_SSH_DIR_PATH = Path("~/.ssh").expanduser()
LASSH_CONFIG_PATH = Path("./lassh.config")
HOME_LASSH_DIR_PATH = Path("~/.lassh").expanduser()
HOME_LASSH_NAMESPACE_PATH = Path("~/.lassh/namespace").expanduser()


def checkFiles():
    """Check if neccesary files exist"""
    # Check if ~/.ssh directory exists
    if (not HOME_SSH_DIR_PATH.exists()):
        puts(colored.red('.ssh/ not found, try `lassh init`'))
        return

    if (not HOME_SSH_CONFIG_PATH.exists()):
        puts(colored.red('.ssh/config file not found, try `lassh init`'))
        return

    # Check if lassh.config file exists in current directory
    if (not LASSH_CONFIG_PATH.exists()):
        puts(colored.red(('lassh.config file not found in current directory'
                          'try `lassh init`')))

    if (not HOME_LASSH_DIR_PATH.exists()):
        puts(colored.red('~.lassh/ not found, try `lassh init`'))

    if (not HOME_LASSH_NAMESPACE_PATH.exists()):
        puts(colored.red('~.lassh/namespace not found, try `lassh init`'))

        return


def deleteInclude():
    # File line modification from:
    # https://stackoverflow.com/questions/4710067/deleting-a-specific-line-in-a-file-python
    # Check if the Include statement already exists
    includeFound = False
    corrupted_configs = set()
    with open(HOME_SSH_CONFIG_PATH, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            lineComponents = str.split(line)
            # Check for Include statments
            if lineComponents and lineComponents[0] == 'Include':
                includePathString = lineComponents[1]
                includePath = Path(includePathString)
                # Check if path indicated by pathstring is a file
                if (not includePath.exists()):
                    corrupted_configs.add(includePathString)
                    puts(colored.yellow(
                        'Found corrupted config {0}, removing'
                        .format(includePathString)))
                    # if it's not then we add it to corrupted_configs and skip
                    continue

                if (os.path.samefile(LASSH_CONFIG_PATH.resolve(),
                                     includePathString)):
                    puts(colored.red(
                        'Deleting include for {0}'.format(includePathString)))
                    includeFound = True
                # If not, preserve the line
                else:
                    f.write(line)

            # if not Include statement, preserve it
            else:
                f.write(line)
        f.truncate()
    # now delete any corrupted configs
    deleteCorruptedConfig(corrupted_configs)

    return includeFound


def deleteCorruptedConfig(corrupted_configs):
    # PASS IN SET OF CONFIG PATHS AND THEN CHECK EACH LINE AGAINST BEING IN IT
    # Include and current lassh.config are the same file
    """
    if (faulty_path and
            os.path.samefile(faulty_path.resolve(),
                             includePathString)):
        puts(colored.red(
            'Deleting include for {0}'.format(includePathString)))
        includeFound = True
    """
    with open(HOME_SSH_CONFIG_PATH, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            lineComponents = str.split(line)
            # Check for Include statments
            if lineComponents and lineComponents[0] == 'Include':
                includePathString = lineComponents[1]
                #  Check if this string isn't corrupted, if so write
                if includePathString not in corrupted_configs:
                    f.write(line)

            # if not Include statement, preserve it
            else:
                f.write(line)
        f.truncate()


@click.group()
def lassh():
    """A tool to help manage per-project ssh_configs"""


@lassh.command()
def init():
    """Checks and creates neccessary files,
    creates lassh.config in current directory"""

    # Check if ~/.ssh directory exists
    if (not HOME_SSH_DIR_PATH.exists()):
        puts('.ssh/ not found, creating')
        Path(HOME_SSH_DIR_PATH).mkdir(parents=True)

    if (not HOME_SSH_CONFIG_PATH.exists()):
        puts('.ssh/config file not found, creating')
        Path(HOME_SSH_CONFIG_PATH).touch()

    # Check if lassh.config file exists in current directory
    if (not LASSH_CONFIG_PATH.exists()):
        puts(colored.green('Creating lassh.config file'))
        Path(LASSH_CONFIG_PATH).touch()

    if (not HOME_LASSH_DIR_PATH.exists()):
        puts(colored.green('Creating ~.lassh/ directory'))
        Path(HOME_LASSH_DIR_PATH).mkdir(parents=True)

    if (not HOME_LASSH_NAMESPACE_PATH.exists()):
        puts(colored.green('Creating ~.lassh/namespace file'))
        Path(HOME_LASSH_NAMESPACE_PATH).touch()

    # Check if the Include statement already exists
    with open(HOME_SSH_CONFIG_PATH, 'r') as f:
        lineSet = set(f.readlines())
        corrupted_configs = set()
        for line in lineSet:
            lineComponents = str.split(line)
            # Check for Include statments
            if lineComponents and lineComponents[0] == 'Include':
                includePathString = lineComponents[1]
                # Check if path indicated by
                # Include and current lassh.config are the same file
                includePath = Path(includePathString)

                # Check if a lassh config no longer exists
                if (not includePath.exists()):
                    corrupted_configs.add(includePathString)
                    puts(colored.yellow(
                        'Found corrupted config {0}, removing'
                        .format(includePathString)))
                    continue

                # Check if global config already points to this file
                if os.path.samefile(LASSH_CONFIG_PATH.resolve(),
                                    includePathString):
                    puts(colored.yellow(
                        'Global ssh_config already includes this file'))

                    # before we exit, clean up the corrupted configs
                    deleteCorruptedConfig(corrupted_configs)
                    return

    # Else, append a new Include statement!
    puts('Adding Include to global ssh_config')
    with open(HOME_SSH_CONFIG_PATH, 'a') as f:
        f.write("Include {0}\n".format(LASSH_CONFIG_PATH.resolve()))
    # Then, cleanup any corrupted configs that were found
    deleteCorruptedConfig(corrupted_configs)
    puts(colored.green('success'))


@lassh.command()
@click.confirmation_option(
    prompt="Are you sure you want to delete your project lassh configuration?")
def teardown():
    """Deletes project lassh configuration and removes associated nicknames
    from the global namespace"""
    checkFiles()
    success = deleteInclude()
    if success:
        puts(colored.green('Deleted include from global ssh_config'))
    else:
        puts(colored.yellow('Include not found in global ssh_config'))

    # Remove nicknames associated with this lassh config.
    config = read_ssh_config(LASSH_CONFIG_PATH.resolve())
    hostnames = set(config.hosts())

    with open(HOME_LASSH_NAMESPACE_PATH, 'r+') as namespace_file:
        names = namespace_file.readlines()
        namespace_file.seek(0)

        for name in names:
            if name.rstrip() not in hostnames:
                namespace_file.write(name)
        namespace_file.truncate()

    # Delete lassh.config file
    LASSH_CONFIG_PATH.unlink()


@lassh.command()
@click.argument('nickname', required=True)
@click.argument('hostname', required=True)
@click.argument('user', default='root')
@click.option('--port', '-p', type=int)
@click.option('--key', '-k', type=click.Path())
def addhost(nickname, hostname, user, port, key):
    """Add a host to your project lassh.config"""
    # Check for requisite files
    checkFiles()

    # Using ssh_conf library, modify hosts
    config = read_ssh_config(LASSH_CONFIG_PATH.resolve())

    # Check for duplicate hosts in local config
    if nickname in config.hosts():
        puts(colored.yellow(
            'Found duplicate host with nickname {0}, cancelling'
            .format(nickname)))
        return

    # Check global namespace for duplicate host
    with open(HOME_LASSH_NAMESPACE_PATH, 'r+') as namespace_file:
        names = namespace_file.readlines()
        names = {name.rstrip() for name in names}
        namespace_file.seek(0)
        if nickname in names:
            puts(colored.red(('Found duplicate host nickname in'
                              'global ssh namespace, cancelling')))
            return

    if (port and key):
        config.add(
            nickname,
            HostName=hostname,
            User=user,
            Port=port,
            IdentityFile=key)
    elif port:
        config.add(nickname, HostName=hostname, User=user, Port=port)
    elif key:
        config.add(nickname, HostName=hostname, User=user, IdentityFile=key)
    else:
        config.add(nickname, HostName=hostname, User=user)

    # append host to namespace file
    with open(HOME_LASSH_NAMESPACE_PATH, 'a') as namespace_file:
        namespace_file.write(''.join([nickname + '\n']))

    puts(colored.green('Adding host {0} as {1} with user {2}')
         .format(hostname, nickname, user))
    config.write(LASSH_CONFIG_PATH.resolve())


@lassh.command()
@click.argument('nickname', required=True)
def deletehost(nickname):
    "Remove a host from your project lassh.config"
    # Check for requisite files
    checkFiles()

    config = read_ssh_config(LASSH_CONFIG_PATH.resolve())

    if nickname not in config.hosts():
        puts(colored.red('Host not found'))
        return

    puts(colored.red('Deleting hostname {0}').format(nickname))
    config.remove(nickname)
    config.write(LASSH_CONFIG_PATH.resolve())

    with open(HOME_LASSH_NAMESPACE_PATH, 'r+') as namespace_file:
        names = namespace_file.readlines()
        namespace_file.seek(0)

        for name in names:
            if name.rstrip() != nickname:
                namespace_file.write(name)
        namespace_file.truncate()
