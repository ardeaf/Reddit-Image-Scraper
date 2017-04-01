import time
from datetime import datetime

import praw

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

    retrieve_time = datetime.now()
    print("Retrieving submissions from {}. Started at {}".format(subreddit_name, time.strftime("%H:%M:%S")))

    reddit = bot_login()
    subreddit = reddit.subreddit(subreddit_name)

    submissions = subreddit.submissions(start=start_date, end=end_date)

    # for each url I add (url, submission_datetime) to ret_list.
    ret_list = [[submission.url, datetime.fromtimestamp(submission.created_utc).strftime('%Y%m%d_%H%M%S_')]
                for submission in submissions
                if submission.url.endswith(exts)]

    if verbose:
        delta = (datetime.now() - retrieve_time).total_seconds()
        print("Retrieval of submissions took {} seconds.  Completed at {}".format(
            str(delta), time.strftime("%H:%M:%S")))

    return ret_list

if __name__ == '__main__':
    reddit = bot_login()
    print(reddit)
