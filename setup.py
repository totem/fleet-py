import sys
from distutils.core import setup

if sys.version_info <= (3, 4):
    error = "ERROR: fleet-sdk requires Python Version 3.4 or above...exiting."
    print(error, file=sys.stderr)
    sys.exit(1)

setup(
    name='fleet-sdk',
    version='0.1.0',
    description='Fleet SDK Wrapper for Python',
    author='Sukrit Khera',
    author_email='',
    url='https://github.com/sukrit007/fleet-sdk',
    license = 'MIT',
    platforms = 'Posix; MacOS X;',
    packages=['scheduler']
)