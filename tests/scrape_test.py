import glob
from datetime import datetime
import pytz
import requests_mock
import os

from hypothesis import given, event
from hypothesis.strategies import integers, text
import unittest.mock as mock
import pytest

from redditimagescraper import scrape


@given(integers(), text(), integers(2005, datetime.now().year))
def test_what_year_hypothesis(random_nums, random_strings, valid_nums):
    # Given random_nums, we should get a ValueError if not with valid range of years.
    event(str(random_nums))
    if random_nums not in list(range(2005, datetime.now().year + 1)):
        with mock.patch('builtins.input', return_value=random_nums):
            with pytest.raises(ValueError):
                scrape.what_year('start', True)

    # Given text, should always get a value error.
    if random_strings.isdigit():
        random_strings = str(int(random_strings))

    with mock.patch('builtins.input', return_value=random_strings):
        event(random_strings)
        if random_strings not in str(list(range(2005, datetime.now().year))):
            with pytest.raises(ValueError):
                scrape.what_year('start', True)

    # Given valid years, should get number back as an integer.
    with mock.patch('builtins.input', return_value=valid_nums):
        event(str(valid_nums))
        assert valid_nums == scrape.what_year('start')

@given(integers(), text(), integers(1, 12))
def test_what_month_hypothesis(random_nums, random_strings, valid_nums):
    # Given random_nums, we should get a ValueError if not with valid range of years.
    # Otherwise we should get back the number in integer form.
    event(str(random_nums))
    if random_nums not in range(1, 13):
        with mock.patch('builtins.input', return_value=random_nums):
            with pytest.raises(ValueError):
                scrape.what_month(True)

    # Given text, should always get a value error.
    event(random_strings)
    if random_strings.isdigit():
        random_strings = str(int(random_strings))

    if random_strings not in str(list(range(1, 13))):
        with mock.patch('builtins.input', return_value=random_strings):
            with pytest.raises(ValueError):
                scrape.what_month(True)

    # Given valid years, should get number back as an integer.
    with mock.patch('builtins.input', return_value=valid_nums):
        event(str(valid_nums))
        assert valid_nums == scrape.what_month(True)

# Given both invalid and valid days, should only return the valid day
@pytest.mark.parametrize('valid_day', [day for day in range(1, 32)])
def test_what_day(valid_day):
    days = ["", " ", "99", "0", "-20", str(10 ^ 10000000), str(valid_day)]

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

# Given valid ints should get the valid date back in epoch time.
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


# Given a list of images, should download each one to folder. Check by looking at filenames in current working dir.
@pytest.mark.parametrize('file', [image for image in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                            "test_images", "*"))])
def test_download_file(file, date_created=datetime.now().strftime('%Y%m%d_%H%M%S')):
    with open(file, "br") as f:
        with requests_mock.Mocker() as adapter:
            file_without_path = os.path.split(file)[1]
            image_url = 'mock://testurl.com/' + file_without_path

            filename = date_created + "_" + image_url.split('/')[-1]

            # Reads the file we opened and stores the byte string in image_content
            image_content = f.read()

            # Registers a mock http request using the byte content above and the image_url
            adapter.register_uri('GET', image_url, content=image_content)

            scrape.download_file(image_url, date_created, True)

            assert filename in glob.glob("*.*")

            # Clean up the directory
            os.remove(filename)


# Given both valid and invalid argument, expect passes on the valid ones and fails on the invalid ones.
@pytest.mark.parametrize('args, expected_args', [
    (['-v', '-as', '-i', '-bd', '1.1.2005', '-ed', '1.1.2005', '-sr', 'hamsters'],
     [True, True, True, '1.1.2005', '1.1.2005', 'hamsters']),
    (['-v', '-as', '-i', '-bd', '1.1.2005', '-sr', 'hamsters'], [True, True, True, '1.1.2005', 'hamsters']),
    ([], [False, False, False]),
    pytest.mark.xfail((['-v', 'test'], [True, False, False])),
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


# Given arguments:
# need at least one -v
# need at least one -sr -bd -ed
# need at least one -as
# need at least one with no args

# patch async.main        to return True
# patch subs_to_download  to return [ [url, date_created], ... ] from the tests/test_images folder

# Look for various verbose inputs when passing in -v, otherwise just the dictionary should match at the end.
# expect our images to be downloaded (delete after testing is completed)
@pytest.mark.parametrize('start, end', [('1.1.2015', '1.1.2015'), ('1.1.2005', datetime.now().strftime('%m.%d.%Y'))])
@pytest.mark.parametrize('args', [['-v', '-as', '-bd', '1.1.2015', '-ed', '1.1.2015', '-sr', 'hamsters'], ['-v'], []])
def test_main(args, start, end, capsys):
    # Default start of our vars that we are looking to check for.
    test_user_vars = {'subreddit': 'hamsters', 'async': False, 'imgur': False, 'verbose': False, 'quick_run': False}

    # Given the presence of -as, -v, -bd, etc. then we expect those to returned True in user_vars.
    if '-as' in args:
        test_user_vars['async'] = True

    if '-bd' in args and '-ed' in args and '-sr' in args:
        start = args[args.index("-bd") + 1]
        end = args[args.index("-ed") + 1]
        test_user_vars['quick_run'] = True

    if '-i' in args:
        test_user_vars['imgur'] = True

    if '-v' in args:
        test_user_vars['verbose'] = True

    start_listed = start.split('.')
    end_listed = end.split('.')

    test_user_vars['begin_epoch'] = datetime(int(start_listed[2]), int(start_listed[0]),
                                             int(start_listed[1]), 0, 0, 0, 000000, pytz.utc).timestamp()

    test_user_vars['end_epoch'] = datetime(int(end_listed[2]), int(end_listed[0]),
                                           int(end_listed[1]), 23, 59, 59, 999999, pytz.utc).timestamp()

    # Inputs that will be passed into the mock.patch('builtins.input') to mock input()
    input_list = [start_listed[2], start_listed[0], start_listed[1], end_listed[2], end_listed[0], end_listed[1]]

    # Update our input list to include the subreddit.
    input_list.append(test_user_vars['subreddit'])

    # Helper lists of files and submissions that we are "downloading"
    files_to_mock_download = [image for image in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                        "test_images", "*"))]
    test_subs_to_download = ['mock://testurl.com/' + filename for filename in files_to_mock_download]

    # ALL THE MOCKS!
    with mock.patch('redditimagescraper.modules.accessreddit.subs_to_download',
                    return_value=[[datetime.now().strftime('%m%d%Y'), submission]
                                 for submission in test_subs_to_download]), \
        mock.patch('builtins.input', side_effect=input_list), \
        mock.patch('redditimagescraper.modules.async.main',        # Not testing Async here, return True if called.
                   return_value=True), \
        mock.patch('redditimagescraper.scrape.download_file',
                   side_effect=[test_download_file(file, datetime.now().strftime('%m%d%Y'))
                                for file in files_to_mock_download]):

        actual_user_vars = scrape.main(args)

        if test_user_vars['verbose']:
            actual_output = capsys.readouterr()[0]
            expected_output = ["downloaded in", "Downloading file", "Downloading started", "Downloading completed"]

            if test_user_vars['async']:
                # No verbosity gets printed in async
                expected_output = []

            for output in expected_output:
                assert output in actual_output

        assert actual_user_vars == test_user_vars
