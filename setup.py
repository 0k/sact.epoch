from setuptools import setup, find_packages


def get_version(version):
    import datetime
    if "dev" in version:
        now = int(datetime.datetime.now().strftime('%Y%m%d%H%M'))
        return "%s-r%d" % (version, now)
    else:
        return version

version = '0.7.0dev'

setup(
    name='sact.epoch',
    version=get_version(version),
    description="",
    long_description=open("README.rst").read() + open("CHANGELOG.rst").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development",
    ],
    keywords='sact time timedelta',
    author='SecurActive SA',
    author_email='opensource@securactive.net',
    url='http://github.com/securactive/sact.epoch',
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
        'z3c.testsetup',
    ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
)
