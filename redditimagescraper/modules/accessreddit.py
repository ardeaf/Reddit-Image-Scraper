import time
from datetime import datetime

import praw
import prawcore.exceptions

from . import config


def bot_login():
    reddit = praw.Reddit(username=config.username,
                         password=config.password,
                         client_secret=config.client_secret,
                         client_id=config.client_id,
                         user_agent="redditimagescraper, created by ardeaf")
                
    return reddit


# Returns a list of urls posted to the subreddit_name between start_date and end_date.
# The list is in the form: [url, date_string], [url, date_string], [url, date_string], ... ]
def subs_to_download(subreddit_name, start_date, end_date, exts, verbose):

    if verbose:
        print("Logging into Reddit.")
        login_time = datetime.now()

    reddit = bot_login()

    if verbose:
        print("Login complete, took {} seconds.".format(datetime.now() - login_time).total_seconds())

    while True:
        if verbose:
            retrieve_time = datetime.now()
            print("Retrieving submissions from {}. Started at {}".format(subreddit_name, time.strftime("%H:%M:%S")))

        subreddit = reddit.subreddit(subreddit_name)
        submissions = subreddit.submissions(start=start_date, end=end_date)

        try:
            # for each url I add (url, submission_datetime) to ret_list.
            # Exceptions in praw get raised when you call from the api object, not when you create it.
            ret_list = [[submission.url, datetime.fromtimestamp(submission.created_utc).strftime('%Y%m%d_%H%M%S')]
                        for submission in submissions
                        if submission.url.endswith(exts)]
            break

        except prawcore.exceptions.Redirect and prawcore.exceptions.BadRequest as e:
            if verbose:
                print("\n!! Exception Raised: {}".format(e))
            subreddit_name = input("{} does not exist. Please re-enter a valid subreddit: ".format(subreddit_name))

    if verbose:
        delta = (datetime.now() - retrieve_time).total_seconds()
        print("Retrieval of submissions took {} seconds.  Completed at {}".format(
            str(delta), time.strftime("%H:%M:%S")))

    return ret_list

if __name__ == '__main__':
    reddit = bot_login()
    print(reddit)
