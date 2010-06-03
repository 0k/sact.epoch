from setuptools import setup, find_packages

def get_version(version):
    try:
        if "dev" in version:
            import os
            from mercurial import hg, ui
            repo = hg.repository(ui.ui(),os.path.abspath(os.curdir))
            return "%s-r%d" % (version, len(repo.changelog)-1)
        else:
            return version
    except:
        return version

version = '0.4.0dev'

setup(
    name='sact.epoch',
    version=get_version(version),
    description="",
    long_description=open("docs/source/overview.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='sact nss4',
    author='SecurActive SA',
    author_email='dev@securactive.net',
    url='www.securactive.net',
    license='SecurActive license',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['sact'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'zope.interface',
        'zope.component',
        'pytz',
    ],
    extras_require={'test': [
        'zope.testing',
        # -*- Extra requirements: -*-
        'sact.test',
    ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
