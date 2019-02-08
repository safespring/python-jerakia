from setuptools import setup,find_packages

setup(
    name='python-jerakia',
    version='0.8.4',
    packages=find_packages(),
    include_package_data=True,
    description='Python client library for Jerakia (https://jerakia.io)',
    author='Jon Ander Novella',
    install_requires=[
        'requests>=2.0',
        'click>=6.7',
        'click-plugins',
        'msgpack',
        'mock',
        'jinja2',
        'pyaml',
        'six',
        'cryptography>=2.2.1',
        'pyOpenSSL',
        'future'
    ],
    entry_points='''
        [console_scripts]
        jerakia=jerakia.cli:main
        [root.plugins]
        plugin=jerakia.cli:main
    ''',
    extras_require = {
        'kcli':  ["kcli"]
    }
)
