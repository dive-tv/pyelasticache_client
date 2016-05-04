#!/usr/bin/env python
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

readme = read('README.rst')

from distutils.core import setup
setup(
  name = 'pyelasticache',
  packages = ['pyelasticache'],
  version = '0.1',
  description = 'A comprehensive, fast, pure Python memcached client',
  long_description=readme,
  author = 'David Fierro, Guillermo Menéndez, N. Angulo y Charles Gordon',
  author_email = 'backend@touchvie.com',
  url = 'https://github.com/touchvie/pymemcache',
  keywords = ['AWS', 'elasticache', 'memcache'],
  classifiers = [],
)
