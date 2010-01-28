import datetime
import time

from .interfaces import ITimeZone

from zope.interface import implements
from zope.component import queryUtility


ZERO=datetime.timedelta(seconds=0)


class UTC(datetime.tzinfo):
    """Represent the UTC timezone.

    From http://docs.python.org/library/datetime.html#tzinfo-objects examples

    XXXvlab: pytz.utc isn't better ?

    """

    implements(ITimeZone)

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __repr__(self):
        return "<TimeZone: UTC>"


class TzSystem(datetime.tzinfo):
    """Get the timezone locale of the system. It is used for datetime object.
    This object get the local DST and utcoffset.

    More explanation about how it is work for utcoffset:

    time.daylight is Nonzero if a DST timezone is defined.
    In this case we have two different values in stdoffset and dstoffset.
    For example for timezone 'Europe/Paris' we have:
    stdoffset = -3600
    dstoffset = -7200

    In `utcoffset` method, we check for the daylight saving or not and adjust
    offset in consequence.

    """

    implements(ITimeZone)

    zero = datetime.timedelta(0)

    #Get the right offset with DST or not
    stdoffset = datetime.timedelta(seconds = -time.timezone)
    if time.daylight:
        dstoffset = datetime.timedelta(seconds = -time.altzone)
    else:
        dstoffset = stdoffset

    #Get the DST adjustement in minutes
    dstdiff = dstoffset - stdoffset

    def utcoffset(self, dt):
        """Return offset of local time from UTC, in minutes
        """

        if self._isdst(dt):
            return self.dstoffset
        else:
            return self.stdoffset

    def dst(self, dt):
        """Return the daylight saving time (DST) adjustment, in minutes
        """

        if self._isdst(dt):
            return self.dstdiff
        else:
            return self.zero

    def tzname(self, dt):
        """Return the time zone name corresponding to the datetime object dt
        """

        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        """Return True or False depending of tm_isdst value

        Convert dt in timestamp, and get time object with this timestamp to get
        the localtime and see if this time is dst or not

        """

        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


class TzTest(datetime.tzinfo):
    """Timezone crafted for tests"""

    implements(ITimeZone)

    def utcoffset(self,dt):
        return datetime.timedelta(hours=0,minutes=5)
    def tzname(self,dt):
        return "GMT +5m"
    def dst(self,dt):
        return datetime.timedelta(0)


DefaultLocalTimeZone = TzSystem()


def TzLocal():
    """Get local timezone with ZCA."""
    return queryUtility(ITimeZone, name='local', default=DefaultLocalTimeZone)
