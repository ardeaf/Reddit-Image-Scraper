import argparse
import asyncio
import sys
import time
from datetime import datetime

import aiofiles
import aiohttp

import redditimagescraper.scrape
from . import accessreddit
from .config import extensions


# Download image.  Function actually downloads every url and saves it onto disk.
# Does not discriminate on what to download.  Saves file with the "date_created"
# parameter and the url.
async def fetch_image(url, date_created, verbose):

    filename = date_created + "_" + str(url).split('/')[-1]

    # Shows what is being downloaded.
    if verbose:
        # Messages for the download time outputs.
        msg_start = 'Downloading file: {}.'
        msg_end = '\t{} downloaded in {} seconds. Completed at {}.'
        print(msg_start.format(filename))
        dl_time = datetime.now()

    # Opens url and a file using aiohttp and aiofiles.
    # Reads the content 1024 chunks at a time so that content is downloaded
    # and written to disk asynchronously. Normal file writing is I/O blocking.
    loop = asyncio.get_event_loop()

    async with aiohttp.ClientSession(loop=loop) as session:
        async with session.get(url) as response:
            async with aiofiles.open(filename, mode='wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    await file.write(chunk)

    # Prints out how long each file took to download.
    # Timing times each co-routine with its own local variables, so there is no
    # mixing up of printing from other co-routines.
    delta = (datetime.now() - dl_time).total_seconds()
    if verbose:
        print(msg_end.format(filename, str(delta), time.strftime("%H:%M:%S")))

    return


# Can easily expand amount of args using the verbosity as a baseline example.
def get_args(args):
    for i in range(len(args)):
        args[i] = str(args[i])

    parser = argparse.ArgumentParser(description="Finds all submissions between "
                                                 "given dates and downloads urls"
                                                 "that end in .jpg, jpeg, and png.")

    parser.add_argument('-v', '--verbose', action='store_true', help='Print verbose output.', default=False)
    parser.add_argument('subreddit', help='Subreddit you intend to scrape.')
    parser.add_argument('begin_date', help='Begin date.')
    parser.add_argument('end_date', help='End date.')

    return parser.parse_args(args)

# Main function.  Get the submissions from the subreddit between the
# specified dates, and then run the parse function on each one.
async def work(args):

    # Get our args stored in parser.
    args = get_args(args)

    # Get the args.
    verbose = args.verbose
    designated_sub_reddit = args.subreddit
    begin_date = args.begin_date
    end_date = args.end_date

    month_b, day_b, year_b = map(int, begin_date.split('.'))
    month_e, day_e, year_e = map(int, end_date.split('.'))

    date_list = redditimagescraper.scrape.convert_dates(year_b, month_b, day_b, year_e, month_e, day_e)

    # Gets the submissions we're going to download.
    subs_to_download = accessreddit.subs_to_download(designated_sub_reddit, date_list, extensions, verbose)

    if verbose:
        total_start_msg = 'Downloading started at {}'
        total_end_msg = 'Downloading completed at {}. Total download time took {} seconds.'
        total_dl_time_start = datetime.now()
        print(total_start_msg.format(time.strftime("%H:%M:%S")))

    # Start throwing in the tasks for our loop to download.
    tasks = [
            asyncio.ensure_future(fetch_image(url, date_created, verbose))
            for url, date_created in subs_to_download
        ]

    # This will make the loop wait for all of the tasks above to finish before finishing work()
    await asyncio.wait(tasks)

    if verbose:
        print(total_end_msg.format(time.strftime("%H:%M:%S"),(datetime.now() - total_dl_time_start).total_seconds()))


def main(args):
    # Start the loop!!!
    loop = asyncio.get_event_loop()
    loop.run_until_complete(work(args))
    loop.close()

if __name__ == "__main__":
    # Calls the main(args) function which starts the loop
    main(sys.argv[1:])
