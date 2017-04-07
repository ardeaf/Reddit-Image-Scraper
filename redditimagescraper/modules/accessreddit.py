import time
from datetime import datetime

import praw
import prawcore.exceptions

from . import config


def reddit_login():
    reddit = praw.Reddit(username=config.username,
                         password=config.password,
                         client_secret=config.client_secret,
                         client_id=config.client_id,
                         user_agent="redditimagescraper, created by ardeaf")

    return reddit


# Returns a list of urls posted to the subreddit_name between start_date and end_date.
# The list is in the form: [url, date_string], [url, date_string], [url, date_string], ... ]
def subs_to_download(subreddit_name, date_list, exts, verbose):

    if verbose:
        print("Logging into Reddit.")
        login_time = datetime.now()

    reddit = reddit_login()

    if verbose:
        print("Login complete, took {} seconds.".format((datetime.now() - login_time).total_seconds()))

    ret_list = list()
    subreddit = reddit.subreddit(subreddit_name)

    if verbose:
        retrieve_time = datetime.now()
        print("Retrieving submissions. Started at {}".format(time.strftime("%H:%M:%S")))

    # date_list has start and end time in epoch for each day between the days we are scraping.
    for date in date_list:
        start_date, end_date = date

        if verbose:
            print("Retrieving submission urls dated {}".format(datetime.utcfromtimestamp(start_date).strftime("%m/%d/%Y")))

        submissions_request = subreddit.submissions(start=start_date, end=end_date)

        while True:
            try:
                ret_list += [[submission.url, datetime.utcfromtimestamp(submission.created_utc).strftime('%Y%m%d_%H%M%S')]
                             for submission in submissions_request
                             if submission.url.endswith(exts)]
                break

            # Check if the subreddit exists
            except prawcore.exceptions.Redirect and prawcore.exceptions.BadRequest as e:
                if verbose:
                    print("\n!! Exception Raised: {}".format(e))
                retrieve_time = datetime.now()
                subreddit_name = input("{} does not exist. Please re-enter a valid subreddit: ".format(subreddit_name))

    if verbose:
        delta = (datetime.now() - retrieve_time).total_seconds()
        print("Retrieval of submissions from /r/{} took {} seconds.  Completed at {}".format(
              subreddit_name, str(delta), time.strftime("%H:%M:%S")))

    return ret_list

if __name__ == '__main__':
    reddit = reddit_login()
    print(reddit)
