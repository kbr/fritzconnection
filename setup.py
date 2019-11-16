from setuptools import setup, find_packages


with open('README.rst') as file:
    the_long_description = file.read()


setup(
    name = 'fritzconnection',
    version = '1.0a1',
    packages = find_packages(),
    license = 'MIT',
    description = 'Communicate with the AVM FritzBox',
    long_description = the_long_description,
    author = 'Klaus Bremer',
    author_email = 'bremer@bremer-media.de',
    url = 'https://github.com/kbr/fritzconnection',
    classifiers = [
        'Development Status :: 4 - Beta',
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
    keywords = 'AVM FritzBox',
    install_requires = [
        'lxml>=4.3.4',
        'requests>=2.22.0',
    ],
    entry_points={'console_scripts': [
        'fritzconnection = fritzconnection.cli.fritzinspection:main',
        'fritzhosts = fritzconnection.cli.fritzhosts:main',
#         'fritzwlan = fritzconnection.fritzwlan:main',
        'fritzmonitor = fritzconnection.cli.fritzmonitor:main',
         'fritzstatus = fritzconnection.cli.fritzstatus:main',
#         'fritzphonebook = fritzconnection.fritzphonebook:main',
#         'fritzcallforwarding = fritzconnection.fritzcallforwarding:main',
#         'fritzcall = fritzconnection.fritzcall:main',
    ]}
)
