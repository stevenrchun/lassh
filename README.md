# ![Clove Hitch Logo](http://stevenchun.me/LaSSH.svg =91x200) LaSSH
A command line tool for managing per-project SSH Configs

## What's a SSH_CONFIG
`ssh` allows the use of a `config` file, usually located in `~/.ssh/config` that allows you to customize `ssh` in a whole host (heh) of ways. One primary use is the creation of aliases for hosts.

However, a single global config file for ssh can quickly become unwieldy and messy (motivating stack exchange: https://serverfault.com/questions/375525/can-you-have-more-than-one-ssh-config-file).

## Introducing LaSSH
A CLI to manage your global config for you and to make using multiple ssh configs easy.

### Getting Started
1. `cd` into your project (or lab or whatever) directory that you want to configure ssh for.

#### Initializing Lassh
2. `lassh init` will create a global config and a project `lassh.config` (if they don't already exist). Note: `lassh.config` files are valid plaintext `.ssh/config` files. It will then link your new or existing `lassh.config` to the global config! But you don't have any new hosts to connect to...

#### Adding Hosts
3. `lassh addhost beepboop computer.dartmouth.edu stevenchun` adds a host now called `beepboop` that points to `stevenchun@computer.dartmouth.edu`. You can also specify a path to identity keys using the `--key` option and a port with the `--port` option. If you leave the user out, it will default to `root`.

#### Deleting Hosts
4. `lassh deletehost beepboop` deletes the host we just made from our local `lassh.config`. (It does not remove the link from our project `lassh.config` to the global config)

#### Teardown
5. `lassh teardown` unlinks and deletes the lassh.config in the current directory from the global config. Warning: this deletes all hosts you have in the project's `lassh.config`

#### Other Operations
Since each `lassh.config` is a valid ssh config file, if you want to add an option like LocalForward, simply add the host and edit the `lassh.config` file to add more options (or contribute to add the relevant feature to LaSSH!!).
