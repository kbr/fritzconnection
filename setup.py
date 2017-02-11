from setuptools import setup, find_packages


with open('pypi_description.rst') as file:
    the_long_description = file.read()


setup(
    name = 'fritzconnection',
    version = '0.6.2',
    packages = find_packages(),
    license = 'MIT',
    description = 'Communicate with the AVM FritzBox',
    long_description = the_long_description,
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords = 'AVM FritzBox',
    install_requires = [
        'lxml>=3.2.5',
        'requests>=2.2.0',
    ],
    entry_points={'console_scripts': ['fritzconnection = fritzconnection.fritzconnection:main',
                                      'fritzhosts = fritzconnection.fritzhosts:main',
                                      'fritzwlan = fritzconnection.fritzwlan:main',
                                      'fritzmonitor = fritzconnection.fritzmonitor:main',
                                      'fritzstatus = fritzconnection.fritzstatus:main',
                                      'fritzphonebook = fritzconnection.fritzphonebook:main']}
)
