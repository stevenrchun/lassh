from setuptools import setup

setup(
    name='lassh',
    author='Steven Chun',
    author_email='schunchicago@gmail.com',
    description=("An open source, MIT-licensed command line tool for managing "
                 "per-project ssh configs."),
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/stevenrchun/lassh',
    version='0.1.1',
    license='LICENSE.txt',
    packages=['lassh', 'lassh.test'],
    install_requires=[
        'Click',
        'sshconf',
        'setuptools',
        'clint',
        'pathlib'
    ],
    entry_points={
        'console_scripts': [
            'lassh=lassh.lassh:lassh'
        ]
    },
)
