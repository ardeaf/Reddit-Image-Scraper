from datetime import datetime

import mock
import pytest

from redditimagescraper import scrape

""""
Testing year, month, and day, make sure to check:
[Lower and higher values,
Space and blank entries,
Positive and negative numbers,
Valid numbers]
"""


@pytest.mark.parametrize('valid_year', [str(year) for year in range(2005, datetime.now().year + 1)])
def test_what_year(valid_year):
    years = ["9999", "0", "", " ", "-2015", "-30", str(10^1000), valid_year]

    with mock.patch('builtins.input', side_effect=years):
        assert scrape.what_year('start') == int(valid_year)


@pytest.mark.parametrize('valid_month', [str(month) for month in range(1, 13)])
def test_what_month(valid_month):
    months = ["9999", "00000", "0", "", " ", "-8", "-1", str(10^1000), valid_month]

    with mock.patch('builtins.input', side_effect=months):
        assert scrape.what_month() == int(valid_month)


@pytest.mark.parametrize('valid_day', [day for day in range(1, 32)])
def test_what_day(valid_day):
    days = ["99", "0", "", " ", "-20", str(10^1000), str(valid_day)]

    if valid_day < 29:
        # Test February, non-leap year, should return valid day.
        month = 2
        year = 2015
    elif valid_day == 29:
        # Test February, leap-year, should return valid_day
        month = 2
        year = 2016
    elif valid_day == 30:
        # Test regular 30-day month (April), should return valid_day
        month = 4
        year = 2016
    elif valid_day == 31:
        # Test regular 31-day month (January), should return valid_day
        month = 1
        year = 2016

    with mock.patch('builtins.input', side_effect=days):
        assert scrape.what_day(month, year) == int(valid_day)
