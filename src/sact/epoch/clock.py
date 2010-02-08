# -*- coding: utf-8 -*-
"""
.. :doctest:

"""


import datetime
import time

from zope.interface import classProvides, implements
from zope.component import queryUtility

from .interfaces import ITime, IClock
from .timezone import UTC, TzLocal
from sact.epoch.utils import datetime_to_timestamp


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
    <Time ...>

    """

    implements(IClock)

    @property
    def time(self):
        """Should return later a Time object"""

        return Time.utcfromtimestamp(self.ts)

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

    Stoping while running should do nothing:

    >>> mc.stop()
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

    Restarting while running should do nothing:

    >>> mc.start()
    >>> mc.is_running
    True

    >>> t3 = mc.ts
    >>> assert t1 < t3, \
    ...    'time %r should be superior to %r and it isn\'t' \
    ...    % (t3, t1)


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

    Setting time should not stop the clock if it was running:

    >>> mc.ts = 20
    >>> mc.is_running
    True


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
        if self.is_running:
            return
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
        if self._ft is not None:
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


class Time(datetime.datetime):
    """Time Factory


    Usage
    =====

    This is quite straightforward to use:

    >>> from sact.epoch.clock import Time
    >>> Time.now()
    <Time ...+00:00>

    Notice that it has a timezone information set.


    We can give a better view thanks to a manageable clock
    as time reference:

    >>> from sact.epoch.clock import ManageableClock
    >>> clock = ManageableClock()

    We will stop the time to epoch:

    >>> clock.stop()
    >>> clock.ts = 0

    Let's set it as reference:

    >>> test.ZCA.registerUtility(clock)

    Now, let's set our TzTest as local timezone, remember it has 5 minute
    difference to UTC:

    >>> from sact.epoch import TzTest
    >>> from sact.epoch.interfaces import ITimeZone

    >>> test.ZCA.registerUtility(TzTest(), ITimeZone, name='local')

    Here is the result of each function:

    >>> Time.now()
    <Time 1970-01-01 00:00:00+00:00>

    >>> Time.now_lt()
    <Time 1970-01-01 00:05:00+00:05>

    Please note that there are 5 minutes of diff to UTC


    Instanciation
    =============

    >>> Time(1980, 01, 01)
    <Time 1980-01-01 00:00:00+00:00>

    """

    classProvides(ITime)

    def __new__(cls, *args, **kwargs):
        if 'tzinfo' not in kwargs and len(args) < 8:
            # XXXjballet: to test
            kwargs['tzinfo'] = UTC()
        return super(Time, cls).__new__(cls, *args, **kwargs)

    def __repr__(self):
        return "<Time %s>" % self

    # XXXjballet: to test
    @classmethod
    def from_datetime(cls, dt):
        """Convert a datetime object with timezone to a Time object

        This method provides a handy way to convert datetime objects to Time
        objects:

        >>> import datetime
        >>> from sact.epoch import UTC
        >>> dt = datetime.datetime(2000, 1, 1, tzinfo=UTC())
        >>> Time.from_datetime(dt)
        <Time 2000-01-01 00:00:00+00:00>

        The provided datetime should contain a timezone information or the
        conversion will fail:

        >>> Time.from_datetime(datetime.datetime.now())
        Traceback (most recent call last):
        ...
        ValueError: no timezone set for ...

        """

        if dt.tzinfo is None:
            raise ValueError("no timezone set for %r" % dt)

        return cls(dt.year, dt.month, dt.day, dt.hour,
                   dt.minute, dt.second, dt.microsecond,
                   dt.tzinfo)

    @staticmethod
    def now():
        utility = queryUtility(IClock, default=DefaultClock)
        return utility.time.replace(tzinfo=UTC())

    @staticmethod
    def now_lt():
        return Time.now().astimezone(TzLocal())

    @classmethod
    def utcfromtimestamp(cls, ts):
        """Return a UTC datetime from a timestamp.

        >>> Time.utcfromtimestamp(0)
        <Time 1970-01-01 00:00:00+00:00>

        """

        dt = super(Time, cls).utcfromtimestamp(ts)
        return dt.replace(tzinfo=UTC())

    @classmethod
    def strptime(cls, value, format, tzinfo):
        """Parse a string to create a Time object.

        >>> from sact.epoch import UTC, TzTest
        >>> Time.strptime('2000-01-01', '%Y-%m-%d', UTC())
        <Time 2000-01-01 00:00:00+00:00>

        >>> tz_test = TzTest()
        >>> Time.strptime('2000-01-01', '%Y-%m-%d', tz_test).tzinfo == tz_test
        True

        """

        dt = super(Time, cls).strptime(value, format)
        return dt.replace(tzinfo=tzinfo)

    def astimezone(self, tz):
        """Convert Time object to another timezone and return a Time object

        This overrides the datetime's method to return a Time object instead of
        a datetime object:

        >>> type(Time.now().astimezone(TzTest()))
        <class 'sact.epoch...Time'>

        """

        dt = super(Time, self).astimezone(tz)
        return self.from_datetime(dt)

    @property
    def timestamp(self):
        """Convert this Time instance in a unix timestamp in UTC

        See sact.epoch.utils

        >>> Time(1970, 1, 1, 0, 0, 1).timestamp
        1

        """
        return datetime_to_timestamp(self)

    @property
    def iso_local(self):
        """Return the iso format in local time

        >>> Time(1970, 1, 1, 1, 1).iso_local
        '1970-01-01 01:06:00+00:05'

        """
        return self.astimezone(TzLocal()).isoformat(" ")
