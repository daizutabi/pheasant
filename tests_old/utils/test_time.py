from datetime import timedelta

import pytest

from pheasant.utils.time import format_timedelta, format_timedelta_human


def test_format_timedelta():
    with pytest.raises(NotImplementedError):
        format_timedelta(timedelta(days=1, seconds=100))
    assert format_timedelta(timedelta(seconds=3670)) == "01:01:10.0"
    assert format_timedelta(timedelta(seconds=3670.3)) == "01:01:10.3"


def test_format_timedelta_human():
    assert format_timedelta_human(timedelta(days=1, seconds=100)) == "24h1min40s"
    assert format_timedelta_human(timedelta(seconds=3670)) == "1h1min10s"
    assert format_timedelta_human(timedelta(seconds=2670)) == "44min30s"
    assert format_timedelta_human(timedelta(seconds=59.564)) == "59.6s"
    assert format_timedelta_human(timedelta(seconds=9.3)) == "9.30s"
    assert format_timedelta_human(timedelta(seconds=0.123)) == "123ms"
    assert format_timedelta_human(timedelta(seconds=0.0453)) == "45.3ms"
    assert format_timedelta_human(timedelta(seconds=0.006544)) == "6.54ms"
    assert format_timedelta_human(timedelta(seconds=3.46e-4)) == "346us"
    assert format_timedelta_human(timedelta(seconds=3.42e-5)) == "34us"
    assert format_timedelta_human(timedelta(seconds=5.934e-6)) == "6us"
    assert format_timedelta_human(timedelta(seconds=5.934e-7)) == "1us"
    assert format_timedelta_human(timedelta(seconds=5.934e-8)) == "<1us"
