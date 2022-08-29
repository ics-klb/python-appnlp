

import os
import sys
import platform
import configparser

from distutils.core import setup

# Make sure 'twisted' doesn't appear in top_level.txt
if sys.version_info[0] < 3:
    raise Exception(
        'You are tying to install ChatterBot on Python version {}.\n'
        'Please install ChatterBot in Python 3 instead.'.format(
            platform.python_version()
        )
    )


config = configparser.ConfigParser()
current_directory = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(current_directory, 'setup.cfg')

config.read(config_file_path)
VERSION = config['botnlp']['version']
AUTHOR = config['botnlp']['author']
AUTHOR_EMAIL = config['botnlp']['email']
URL = config['botnlp']['url']

try:
    from setuptools.command import egg_info
    egg_info.write_toplevel_names
except (ImportError, AttributeError):
    pass
else:
    def _top_level_package(name):
        return name.split('.', 1)[0]

    def _hacked_write_toplevel_names(cmd, basename, filename):
        pkgs = dict.fromkeys(
            [_top_level_package(k)
                for k in cmd.distribution.iter_distribution_names()
                if _top_level_package(k) != "twisted"
            ]
        )
        cmd.write_file("top-level names", filename, '\n'.join(pkgs) + '\n')

    egg_info.write_toplevel_names = _hacked_write_toplevel_names

with open('README.txt') as file:
    long_description = file.read()

setup(name='botnlp',
      version=VERSION,
      description='BotNlp, a twisted botNlp server.',
      long_description=long_description,
      author='Zherebyatyev Denys',
      author_email=AUTHOR_EMAIL,
      zip_safe=False,
      url=URL,
      packages=['botnlp','botnlp.service','botnlp.hubs', 'botnlp.nlu', 'twisted.plugins'],
      package_dir={'botnlp': 'botnlp'},
      package_data={'twisted.plugins': ['twisted/plugins/botnlp.py']},
      include_package_data=True
      # python_requires = '>=3.4, <=3.8'
)
