from datetime import timedelta

from pheasant.jupyter.renderer import format_timedelta


def test_format_timedelta():
    assert format_timedelta(timedelta(days=1, seconds=100)) == "24h1min40s"
    assert format_timedelta(timedelta(seconds=3670)) == '1h1min10s'
    assert format_timedelta(timedelta(seconds=2670)) == '44min30s'
    assert format_timedelta(timedelta(seconds=59.564)) == '59.6s'
    assert format_timedelta(timedelta(seconds=9.3)) == '9.30s'
    assert format_timedelta(timedelta(seconds=0.123)) == '123ms'
    assert format_timedelta(timedelta(seconds=0.0453)) == '45.3ms'
    assert format_timedelta(timedelta(seconds=0.006544)) == '6.54ms'
    assert format_timedelta(timedelta(seconds=3.46e-4)) == '346us'
    assert format_timedelta(timedelta(seconds=3.42e-5)) == '34us'
    assert format_timedelta(timedelta(seconds=5.934e-6)) == '6us'
    assert format_timedelta(timedelta(seconds=5.934e-7)) == '1us'
    assert format_timedelta(timedelta(seconds=3.934e-7)) == '<1us'
