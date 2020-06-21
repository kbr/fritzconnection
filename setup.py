from setuptools import setup, find_packages


with open('README.rst') as file:
    the_long_description = file.read()


setup(
    name = 'fritzconnection',
    version = '1.3.0',
    packages = find_packages(exclude=['*.tests']),
    license = 'MIT',
    description = 'Communicate with the AVM FRITZ!Box',
    long_description = the_long_description,
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
