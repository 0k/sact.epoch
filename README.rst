
sact.epoch is a Python library using Zope Component Architecture providing 
legacy ``datetime.datetime`` subclass that allows a simple time abstraction
mecanism, allowing code that would use it as reference to be diverted both 
on the local time zone and the real time.


INSTALLATION
============

For installation issue please refer to INSTALL.


DEVELOPPEMENT
=============

You can test or use this code simply by launching::

  python bootstrap.py
  buildout

This will install all dependency needed by this code to start coding.


TEST
----

Test framework is available through standard z3c.testsetup mecanism::

  bin/test


DOC
---

Complete documentation can be generated thanks to::

  bin/doc
