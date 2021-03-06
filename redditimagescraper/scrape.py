import sys

import argparse
import time
from datetime import datetime, timedelta, date

import requests
import pytz

from redditimagescraper.modules import async
from redditimagescraper.modules import accessreddit
from redditimagescraper.modules import config

# Error msg. Global for now.
error_msg = "\n\t{} is an invalid {}."


# Returns subreddit that user wishes to scrape.
def subreddit():
    subreddit_name = input('www.reddit.com\\r\\')

    return subreddit_name


# Returns valid number of days in given month and year.
def num_days(month, year):
    days_dict = {1: 31, 2: 28, 3: 31,
                 4: 30, 5: 31, 6: 30,
                 7: 31, 8: 31, 9: 30,
                 10: 31, 11: 30, 12: 31}

    # Leap years.
    if year % 4 == 0:
        days_dict[2] = 29

    return days_dict[month]


# Ask user input, returns year
def what_year(start_or_end, debug=False):
    while True:
        year_str = input('\nEnter the year you would like to {} your range: '.format(start_or_end))
        try:
            # Catch the error if the user doesn't enter a convertable string.
            year = int(year_str)

            # We only want years between 2005 and today's year.
            if year in range(2005, int(datetime.now().year + 1)):
                break
            else:
                print(error_msg.format(year_str, 'year'))
                if debug:
                    raise ValueError
        except ValueError as e:
            print(error_msg.format(year_str, 'year'))
            if debug:
                raise e

    return year


# Get start month
def what_month(debug=False):
    while True:
        str_month = input('\nEnter month: ')
        try:
            month = int(str_month)
            if month in range(1, 13):
                # SUCCESS!
                break
            else:
                print(error_msg.format(str_month, 'month'))
                if debug:
                    raise ValueError
        except ValueError as e:
            print(error_msg.format(str_month, 'month'))
            if debug:
                raise e

    return month


# Get start day
def what_day(month, year, debug=False):
    days_in_month = num_days(month, year)
    while True:
        day_str = input('\nEnter day: ')
        try:
            day = int(day_str)
            if day in range(1, days_in_month + 1):
                # SUCCESS!
                break
            else:
                print(error_msg.format(day, 'day'))
                if debug:
                    raise ValueError
        except ValueError as e:
            print(error_msg.format(day_str, 'day'))
            if debug:
                raise e

    return day


# Helper generator for convert_dates.  Given a start and end date, yields start time and end time for each day in epoch.
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        date = start_date + timedelta(n)

        begin_datetime = datetime(date.year, date.month, date.day, 0, 0, 0, 000000, pytz.utc).timestamp()

        end_datetime = datetime(date.year, date.month, date.day, 23, 59, 59, 999999, pytz.utc).timestamp()

        yield [begin_datetime, end_datetime]


# Convert the given start and end date into a list of days in epoch time.
def convert_dates(year_b, month_b, day_b, year_e, month_e, day_e):

    # This list will contain days by their epoch start time and end time: [[epoch_start, epoch end], ...]
    epoch_date_range_list = list()

    for single_date_by_epoch in daterange(date(year_b, month_b, day_b), date(year_e, month_e, day_e)):
        epoch_date_range_list.append(single_date_by_epoch)

    return epoch_date_range_list


# Take user input and convert to epoch time
def get_user_input():
    # Start Date

    # Dictionary where we will store all of the dates.
    dates = {'year_b': what_year('start'), 'month_b': what_month()}

    dates['day_b'] = what_day(dates['month_b'], dates['year_b'])

    start_date = str(dates['month_b']) + "." + str(dates['day_b']) + "." + str(dates['year_b'])
    print("\nStart date is: {}.\n".format(start_date))

    # End Date

    dates['year_e'] = what_year("end")

    dates['month_e'] = what_month()

    dates['day_e'] = what_day(dates['month_e'], dates['year_e'])

    end_date = str(dates['month_e']) + "." + str(dates['day_e']) + "." + str(dates['year_e'])

    print("\nEnd date is: {}.\n".format(end_date))

    # Dictionary where we will store the user's input
    print('\nEnter subreddit you wish to scrape: ')

    user_vars = {'subreddit': subreddit(), 'start_date': start_date, 'end_date': end_date,
                 'epoch_date_range': convert_dates(int(dates['year_b']), int(dates['month_b']), int(dates['day_b']),
                                                   int(dates['year_e']), int(dates['month_e']), int(dates['day_e']))}

    return user_vars


# Download the file for a given url.
# File name is date created and the filename.
# If verbose is True the script prints the name of the file being downloaded and file download time.
def download_file(url, date_created, verbose):
    filename = date_created + "_" + str(url).split('/')[-1]

    if verbose:
        download_started_message = 'Downloading file: {}.'
        download_finished_message = '\t{} downloaded in {} seconds.'
        print(download_started_message.format(filename))

    with open(filename, "wb") as file:

        dl_time = datetime.now()

        response = requests.get(str(url))
        file.write(response.content)

        delta = (datetime.now() - dl_time).total_seconds()

        if verbose:
            print(download_finished_message.format(filename, str(delta)))


# Can easily expand amount of args using the verbosity as a baseline example.
def parse_args(args):
    parser = argparse.ArgumentParser(description="Finds all submissions between "
                                                 "given dates and downloads urls"
                                                 "that end in .jpg, jpeg, and png.")

    # Add arguments here.
    parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose output.', default=False)
    parser.add_argument('-as', '--async', action='store_true', help='Run async version of code. Should be faster.')
    parser.add_argument('-i', '--imgur', action='store_true', help='Download images from imgur albums as well.')
    parser.add_argument('-bd', '--begin-date', help='Begin date')
    parser.add_argument('-ed', '--end-date', help='End date.')
    parser.add_argument('-sr', '--subreddit', help='Subreddit.')

    # Return the parse object.
    return parser.parse_args(args)


# Main function.
def main(args):
    # Get our args stored in parser.
    parser = parse_args(args)
    verbose = parser.verbose
    begin_date = parser.begin_date
    end_date = parser.end_date
    subreddit = parser.subreddit

    # Check if user passed in their own arguments in the command line and update user_vars dict appropriately.
    if begin_date is not None and end_date is not None and subreddit is not None:
        month_b, day_b, year_b = map(int, begin_date.split('.'))
        month_e, day_e, year_e = map(int, end_date.split('.'))

        user_vars = {'epoch_date_range': convert_dates(year_b, month_b, day_b, year_e, month_e, day_e),
                     'subreddit': subreddit, 'quick_run': True, 'start_date': begin_date, 'end_date': end_date}

    else:
        # Get our user's input for which subreddit and dates they wish to use using the tedious get_user_input function
        user_vars = get_user_input()

        # Didn't do a quick run, so set that value to False.
        user_vars['quick_run'] = False

    # Do future imgur stuff here.
    user_vars['imgur'] = parser.imgur

    print("\nDownloading all {} from /r/{} between dates {} and {}".format(
        str(config.extensions), str(user_vars['subreddit']), user_vars['start_date'], user_vars['end_date']))

    if parser.async:
        args = [user_vars['subreddit'], user_vars['start_date'], user_vars['end_date']]
        # Gotta add in the '-v' argument if user passed it in.
        if verbose:
            user_vars['verbose'] = True
            # Appending -v arg to our call to async since it needs our args added to it again.
            args.append('-v')

        async.main(args)

        # Update user_vars to indicate that we ran the async module.
        user_vars['async'] = True
        print("Scraping complete.")
        return user_vars
    else:
        # Didn't run async, so set that to false.
        user_vars['async'] = False

    # Get the subs to download from accessreddit
    subs_to_download = accessreddit.subs_to_download(user_vars['subreddit'],
                                                     user_vars['epoch_date_range'],
                                                     config.extensions, verbose)

    if verbose:
        total_start_msg = 'Downloading started at {}'
        total_end_msg = 'Downloading completed at {}. Total download time was {} seconds.'
        total_dl_time_start = datetime.now()
        print(total_start_msg.format(time.strftime("%H:%M:%S")))
        user_vars['verbose'] = True
    else:
        user_vars['verbose'] = False

    # This is the actual downloading part.
    for sub_urls in subs_to_download:
        url = sub_urls[0]
        date_created = sub_urls[1]
        download_file(url, date_created, verbose)

    if verbose:
        print(total_end_msg.format(time.strftime("%H:%M:%S"), (datetime.now() - total_dl_time_start).total_seconds()))

    print("Scraping complete.")
    return user_vars

if __name__ == "__main__":
    test = sys.argv[1:]
    main(sys.argv[1:])
