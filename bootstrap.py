import sys
import urllib

version = '1.5.2'
base_url = 'http://dist.rd.securactive.lan/python/bootstrap'

bootstrap_source = base_url + '/bootstrap-%s.py' % version
setuptools_source = base_url + '/ez_setup-%s.py' % version
distribute_source = base_url + '/distribute_setup-%s.py' % version

pypi_url = base_url + '/dist'

sys.argv.extend([
    "--setup-source", distribute_source,
    "--download-base", pypi_url,
    "--version", version,
])

fp = urllib.urlopen(bootstrap_source)
exec fp.read()
