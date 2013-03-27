# -*- coding: utf-8 -*-

from setuptools import setup, find_packages, Command
import sys, os

version = '0.1'

tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-pep8',
    'pytest-xdist',
]

install_requires = [
    'python-novaclient',
    'netaddr',
    'pycrypto',
]

dependency_links = [
]


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        errno = subprocess.call(['make', 'test'])
        raise SystemExit(errno)


setup(name='forest',
      version=version,
      description="description",
      long_description="""\
long description""",
      classifiers=[],
      keywords='OpenStack forest',
      author='atomd',
      author_email='dwb319@gmail.com',
      url='forest.homepage.com',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      dependency_links=dependency_links,
      cmdclass={'test': PyTest},
      extras_require={
          'testing': tests_require,
          #'development': development_requires,
          #'docs': docs_require,
      },
      entry_points="""
      [console_scripts]
          init_forest_db = forest.scripts.database:init_db
          drop_forest_db = forest.scripts.database:drop_db

      # -*- Entry points: -*-
      """,
      )
