import glob
from datetime import datetime
import pytz
import requests_mock
import os

import mock
import pytest

from redditimagescraper import scrape

# Should get the "valid_year" result back, which are years from 2005 -> this year
@pytest.mark.parametrize('valid_year', [str(year) for year in range(2005, datetime.now().year + 1)])
def test_what_year(valid_year):
    years = ["9999", "0", "", " ", "-2015", "-30", str(10 ^ 1000), valid_year]

    with mock.patch('builtins.input', side_effect=years):
        assert scrape.what_year('start') == int(valid_year)


# Should get valid months (1 -> 12)
@pytest.mark.parametrize('valid_month', [str(month) for month in range(1, 13)])
def test_what_month(valid_month):
    months = ["9999", "00000", "0", "", " ", "-8", "-1", str(10 ^ 1000), valid_month]

    with mock.patch('builtins.input', side_effect=months):
        assert scrape.what_month() == int(valid_month)


# Should get valid days, depending on month and leap year.
@pytest.mark.parametrize('valid_day', [day for day in range(1, 32)])
def test_what_day(valid_day):
    days = ["99", "0", "", " ", "-20", str(10 ^ 1000), str(valid_day)]

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


# Pass in lists of invalid/valid years>months>days, should get the valid result back.
@pytest.mark.parametrize('test_input, expected', [
    (['2010-1-1', '2010-1-1'], [1262304000.0, 1262390399.999999]),
    (['2015-1-1', '2016-2-29'], [1420070400.0, 1456790399.999999]),
    (['2005-12-31', 'today'], [1135987200.0, 'today'])
])
def test_get_user_input(test_input, expected):
    # If user puts in today's date, should get the epoch time corresponding to the end of today UTC.
    if 'today' in test_input:
        date_today = datetime.utcnow().strftime("%Y-%m-%d")
        test_input[1] = date_today

        date_today_list = date_today.split('-')
        expected[1] = datetime(int(date_today_list[0]), int(date_today_list[1]),
                               int(date_today_list[2]), 23, 59, 59, 999999, pytz.utc).timestamp()

    date_begin = test_input[0]
    date_begin_list = date_begin.split('-')

    years_b = ["9999", "00000", "0", "", " ", "-2015", "-30", date_begin_list[0]]
    months_b = ["9999", "00000", "0", "", " ", "-8", "-1", date_begin_list[1]]
    days_b = ["99", "00000", "0", "", " ", "-8", "-20", date_begin_list[2]]

    date_end = test_input[1]
    date_end_list = date_end.split('-')

    years_e = ["9999", "00000", "0", "", " ", "-2015", "-30", date_end_list[0]]
    months_e = ["9999", "00000", "0", "", " ", "-8", "-1", date_end_list[1]]
    days_e = ["99", "00000", "0", "", " ", "-8", "-20", date_end_list[2]]

    subreddit = ['hamsters']

    user_input = years_b + months_b + days_b + years_e + months_e + days_e + subreddit

    with mock.patch('builtins.input', side_effect=user_input):
        assert scrape.get_user_input() == {'begin_epoch': expected[0],
                                           'end_epoch': expected[1],
                                           'subreddit': 'hamsters'}


# Should pass if filenames match.
@pytest.mark.parametrize('file', [image for image in glob.glob("tests/test_images/*.*")])
def test_download_file(file):
    with open(file, "br") as f:
        with requests_mock.Mocker() as adapter:
            image_url = 'mock://testurl.com/' + file
            print(image_url)
            date_created = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = date_created + "_" + image_url.split('/')[-1]

            # Reads the file we opened and stores the byte string in image_content
            image_content = f.read()

            # Registers a mock http request using the byte content above and the image_url
            adapter.register_uri('GET', image_url, content=image_content)

            scrape.download_file(image_url, date_created, True)

            assert filename in glob.glob("*.*")

            # Clean up the directory
            os.remove(filename)

# Should pass if arguments are thrown in, and fail when invalid arguments are thrown in.
@pytest.mark.parametrize('args, expected_args', [
    (['-v', '-as', '-i', '-bd', '1.1.2005', '-ed','1.1.2005', '-sr','hamsters'],
     [True, True, True,  '1.1.2005', '1.1.2005', 'hamsters']),
    (['-v', '-as', '-i', '-bd', '1.1.2005', '-sr', 'hamsters'], [True, True, True,  '1.1.2005', 'hamsters']),
    ([], [False, False, False]),
    pytest.mark.xfail((['-v','test'], [True, False, False])),
    pytest.mark.xfail((['-bd'], [False, False, False]))
])
def test_parse_args(args, expected_args):

    parser = scrape.parse_args(args)

    arg_list = list()

    args.append(parser.verbose)
    args.append(parser.async)
    args.append(parser.imgur)
    args.append(parser.begin_date)
    args.append(parser.end_date)
    args.append(parser.subreddit)

    for arg, expected_arg in zip(arg_list, expected_args):
        assert arg == expected_arg


def test_main(args):
    # Should end up with files in directory.





































