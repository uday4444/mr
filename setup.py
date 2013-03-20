from setuptools import setup, find_packages
import sys, os

version = '0.1'

dependency_links = [
]

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
      install_requires=[
          'python-novaclient',
      ],
      dependency_links=dependency_links,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
