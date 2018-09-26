from setuptools import setup

setup(
    name='lassh',
    version='0.1.0',
    packages=['lassh'],
    install_requires=[
        'Click',
        'sshconf',
        'setuptools'
    ],
    entry_points={
        'console_scripts': [
            'lassh=lassh.__main__:main'         
        ]
    },
)
