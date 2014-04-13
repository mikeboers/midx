from setuptools import setup, find_packages

setup(
    
    name='midx',
    version='0.1.0',
    description='Mini sequence index.',
    url='http://github.com/mikeboers/midx',
    
    packages=find_packages(exclude=['tests', 'tests.*']),
    
    author='Mike Boers',
    author_email='midx@mikeboers.com',
    license='BSD-3',

    install_requires=[
        'watchdog',
    ],
    
    entry_points={
        'midx_commands': [
            'list = midx.commands.list:list_',
            'scan = midx.commands.scan:scan',
            'watch = midx.commands.watch:watch',
        ],
        'console_scripts': [
            'midx = midx.commands.main:main',
        ],
    },

)
