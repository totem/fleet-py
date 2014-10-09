from distutils.core import setup

with open('requirements.txt') as req_file:
    requirements = req_file.read().splitlines()

setup(
    name='fleet-py',
    install_requires=requirements,
    version='0.1.0',
    description='Fleet SDK Wrapper for Python',
    author='Sukrit Khera',
    author_email='',
    url='https://github.com/totem/fleet-py',
    license='MIT',
    platforms='Posix; MacOS X;',
    packages=['fleet', 'fleet.client', 'fleet.deploy']
)
