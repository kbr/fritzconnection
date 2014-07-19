from setuptools import setup, find_packages

setup(
    name = 'fritzconnection',
    version = '0.4.5',
    packages = find_packages(),
    license = 'MIT',
    description = 'Communicate with the AVM FritzBox',
    author = 'Klaus Bremer',
    author_email = 'bremer@bremer-media.de',
    url = 'https://bitbucket.org/kbr/fritzconnection',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords = 'AVM FritzBox',
    install_requires = [
        'lxml>=3.2.5',
        'requests>=2.2.0',
    ],
)
