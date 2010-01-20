# -*- coding: utf-8 -*-
"""
.. :doctest:
"""


import datetime
import time

from zope.interface import classProvides, implements
from zope.component import queryUtility

from .interfaces import ITime, IClock


class Clock(object):
    """Time Factory

    Will only serve the current time.

    Usage
    =====

    >>> from sact.epoch.clock import Clock
    >>> c = Clock()

    We can use property 'ts' to get the timestamp and it should change very
    accurately at each call:

    >>> c.ts < c.ts
    True

    If we need a full object we should use:

    >>> c.time
    datetime.datetime(...)

    """

    implements(IClock)

    @property
    def time(self):
        """Should return later a Time object"""
        return datetime.datetime.utcfromtimestamp(self.ts)

    @property
    def ts(self):
        return time.time()


class ManageableClock(Clock):
    """Creates a manageable time object

    Can be used to control what time it is. Start/Stop method can
    start/stop time, and wait/set will alter current time.

    Usage
    =====

    >>> from sact.epoch.clock import ManageableClock
    >>> mc = ManageableClock()

    Stopping time
    -------------

    >>> mc.stop()
    >>> t1 = mc.ts
    >>> t2 = mc.ts
    >>> assert t1 == t2, 'time %r should be equal to %r and it isn\'t' \
    ...              % (t1, t2)
    >>> mc.is_running
    False

    Restarting time
    ---------------

    >>> mc.start()
    >>> t1 = mc.ts
    >>> t2 = mc.ts
    >>> assert t1 != t2, 'time %r should NOT be equal to %r and it is' \
    ...              % (t1, t2)
    >>> mc.is_running
    True

    Setting time
    ------------

    >>> mc.stop()
    >>> mc.ts = 0
    >>> mc.ts
    0
    >>> mc.start()
    >>> ts = mc.ts
    >>> assert ts > 0, \
    ...    'clock should have been running and thus timestamp should be greater than 0.' \
    ...    'It was %r.' % ts

    Altering time
    -------------

    >>> mc.stop()
    >>> mc.ts = 20
    >>> mc.ts += 10
    >>> mc.ts
    30
    >>> mc.start()
    >>> ts = mc.ts
    >>> assert ts > 30, \
    ...    'clock should have been running and thus timestamp should be greater than 30.' \
    ...    'It was %r.' % ts

    Altering with wait
    ------------------

    >>> mc.stop()
    >>> mc.ts = 0
    >>> mc.wait(minutes=5)
    >>> mc.ts
    300
    >>> mc.start()
    >>> mc.wait(minutes=5)
    >>> ts = mc.ts
    >>> assert ts > 600, \
    ...    'clock should have been running and thus timestamp should be greater than 600.' \
    ...    'It was %r.' % ts

    """

    implements(IClock)

    def __init__(self):
        self.delta = 0
        self._ft = None ## freezed time

    def start(self):
        ## use _ft to calculate the time delta
        self.delta = self.ts - self.delta - self._ft
        self._ft = None

    def stop(self):
        ## save real current time
        self._ft = self.ts - self.delta

    @property
    def is_running(self):
        return self._ft is None

    def get_ts(self):
        if not self.is_running:
            return self._ft
        return time.time() + self.delta

    def set_ts(self, value):
        self.delta = value - time.time()
        # don't forget to update self._ft
        self._ft = value

    ts = property(get_ts, set_ts)

    def wait(self, timedelta=None, **kwargs):
        """Provide a convenient shortcut to alter the current time

        timedelta can be an int/float or a timedelta objet from datetime.timedelta

        """
        if timedelta is None:
            timedelta = datetime.timedelta(**kwargs)

        if isinstance(timedelta, datetime.timedelta):
            secs = timedelta.days * 86400 + timedelta.seconds
        else:
            secs = int(timedelta)

        self.ts += secs


DefaultClock = Clock()


class Time(object):
    """Time Factory

    >>> from sact.epoch.clock import Time
    >>> Time.now()
    datetime.datetime(...)

    """

    classProvides(ITime)

    @staticmethod
    def now():
        return queryUtility(IClock, default=DefaultClock).time
