from setuptools import setup

from sys import version
if version < '2.6.0':
    raise Exception("This module doesn't support any version less than 2.6")

import sys
sys.path.append("./test")

with open('README.rst', 'r') as f:
    long_description = f.read()

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    "Programming Language :: Python",
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.0',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
    'Topic :: Software Development :: Libraries :: Python Modules'
]


setup(
    author='Keita Oouchi',
    author_email='keita.oouchi@gmail.com',
    url='https://github.com/ghostreet/chainreaction',
    name='chainreaction',
    version='0.2.0',
    package_dir={"":"src"},
    packages=['chainreaction'],
    test_suite="test_reactor.suite",
    license='BSD License',
    classifiers=classifiers,
    description='Wrapper module which provides iterable object with infix style method chaining.',
    long_description=long_description,
)
