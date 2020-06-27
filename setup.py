import os
import re
from setuptools import setup, find_packages


def get_long_description():
    with open('README.rst') as file:
        return file.read()


def get_version():
    path = os.path.join('fritzconnection', '__init__.py')
    with open(path) as file:
        content = file.read()
    mo = re.search(r'\n\s*__version__\s*=\s*[\'"]([^\'"]*)[\'"]', content)
    if mo:
        return mo.group(1)
    raise RuntimeError(f'Unable to find version string in {path}')


setup(
    name = 'fritzconnection',
    version = get_version(),
    packages = find_packages(exclude=['*.tests']),
    license = 'MIT',
    description = 'Communicate with the AVM FRITZ!Box',
    long_description = get_long_description(),
    author = 'Klaus Bremer',
    author_email = 'bremer@bremer-media.de',
    url = 'https://github.com/kbr/fritzconnection',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords = 'AVM FRITZ!Box fritzbox fritz',
    python_requires = ">= 3.6",
    install_requires = [
        'requests>=2.22.0',
    ],
    entry_points={'console_scripts': [
        'fritzconnection = fritzconnection.cli.fritzinspection:main',
        'fritzcall = fritzconnection.cli.fritzcall:main',
        'fritzhomeauto = fritzconnection.cli.fritzhomeauto:main',
        'fritzhosts = fritzconnection.cli.fritzhosts:main',
        'fritzphonebook = fritzconnection.cli.fritzphonebook:main',
        'fritzstatus = fritzconnection.cli.fritzstatus:main',
        'fritzwlan = fritzconnection.cli.fritzwlan:main',
    ]}
)
