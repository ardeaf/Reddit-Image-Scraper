# redditimagescraper

Downloads images from specified subreddit between specified dates. Default downloads all images that are jpg or png, but users can add more.

Based off a project by the same name from /u/2hands10fingers, /u/Joe_Anonimist, /u/iakovosbelonias

## Installation

Working on getting this project into PyPi. For now, just:
Clone repo, go into directory, make a python 3 virtual environment, install requirements.

```
git clone https://github.com/ardeaf/reddit-image-scraper.git
cd reddit-image-scraper
virtualenv -p python3 venv
source venv/bin/activate 	# linux
venv\Scripts\activate		# Windows
pip install -r requirements.txt
pip install -e .		# Gotta do this if you cloned the repo
```

## Accessing Reddit

You will then need to add in your reddit credentials to `config.sample.py` and change the filename to `config.py`.  Then move it into the `redditimagescraper/modules` directory.

To get `client_id` and `client_secret` you must log into reddit, go to preferences > apps and then "create another app" at the bottom.  You can name the app whatever you want, and you can also just make it a *personal use script*. 

Once you create it, `client_id` should be the long randomized string underneath the bolded **appname**.  `client_secret` below that next to *secret*. Paste those two strings into the config.py file in quotes.

## Usage

Simply run `python scrape.py` from inside the `reddit-image-scraper/redditimagescraper` directory.

It currently downloads to whatever directory you ran the script from. If you want to download to another directory you just need to run it with the path inserted from the directory.  For example, to download scraped images to an example `/images/` directory, go to it: 

`cd <path>/<to>/<images>/images/`

Activate your virutal environment (if you have one):
`source <path>/<to>/reddit-image-scraper/venv/bin/activate`

Run the script:
`python <path>/<to>/reddit-image-scraper/redditimagescraper/scrape.py <args>`

### Arguments:
```
-v Verbose output.
-as Downloads asynchronously. Extreme speed increase. Will probably max out your bandwidth.
-bd, -ed, -sr These three have to be passed together.  Allows inputting scrape info from the cli.
-bd is for begin date, -ed is for end date, and -sr is for the subreddit.
-h For more info on args
```

## Tests

If you'd like to contribute or run tests you'll need to install the dev requirements: `pip install -r dev-requirements.txt`
Then run pytest from the root directory (above tests)

## Contributors

Once you install the dev requirements, simply make your own feature branches and submit pull requests.  My tests aren't very rigorous at the moment so be sure your code works by passing both '-v -as' and just '-v' as arguments.

## License

View the license file for more information. You can basically do anything you'd like to the code as long as you make sure your code maintains the same license. 

