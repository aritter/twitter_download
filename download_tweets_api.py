# From Semeval 2014 Task 7
# http://alt.qcri.org/semeval2014/task9/index.php?id=data-and-tools
# Modified by Samuel Leeman-Munk


import argparse
import datetime
import urllib
from twitter import *
import os
import signal
import time

start_time = time.time()
print("Started at", str(datetime.datetime.now()))


# The three-second timeout prevents the download from hanging
# from https://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish
class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, type, value, traceback):
        signal.alarm(0)


parser = argparse.ArgumentParser(description="downloads tweets")
parser.add_argument('--partial', dest='partial', default=None, type=argparse.FileType('r'))
parser.add_argument('--dist', dest='dist', default=None, type=argparse.FileType('r'), required=True)
parser.add_argument('--output', dest='outputpath', default=None, type=str, required=True)

args = parser.parse_args()

CONSUMER_KEY = 'JEdRRoDsfwzCtupkir4ivQ'
CONSUMER_SECRET = 'PAbSSmzQxbcnkYYH2vQpKVSq2yPARfKm0Yl6DrLc'

MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
if not os.path.exists(MY_TWITTER_CREDS):
    oauth_dance("Semeval sentiment analysis", CONSUMER_KEY, CONSUMER_SECRET, MY_TWITTER_CREDS)
oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

if os.path.exists(args.outputpath):
    raise IOError("Cannot overwrite existing output file. Delete or move the file or pick a different output path")

with open(args.outputpath, 'w') as output:
    cache = {}
    if args.partial != None:
        for line in args.partial:
            fields = line.strip().split("\t")
            text = fields[-1]
            sid = fields[0]
            cache[sid] = text

    for i, line in enumerate(args.dist):
        if i % 1 == 0:
            print("\r{}".format(i), end="\t")
        fields = line.strip().split('\t')
        sid = fields[0]
        uid = fields[1]

        while not sid in cache:
            try:
                with timeout(seconds=3):
                    text = t.statuses.show(_id=sid)['text'].replace('\n', ' ').replace('\r', ' ')

                cache[sid] = text
            except TwitterError as e:
                if e.e.code == 429:
                    rate = t.application.rate_limit_status()
                    reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                    now = datetime.datetime.today()
                    future = datetime.datetime.fromtimestamp(reset)
                    seconds = (future - now).seconds + 1
                    if seconds < 10000:
                        print("Rate limit exceeded, sleeping for %s seconds until %s\n" % (seconds, future))
                        time.sleep(seconds)
                else:
                    cache[sid] = 'Not Available'
            except TimeoutError as e:
                print("Timed out. Trying again.")
            except urllib.error.URLError as e:
                print("URLError. Trying again")
        text = cache[sid]

        output.write("\t".join(fields + [text]) + '\n')

elapsed_time = time.time() - start_time
print()
print("download time:", datetime.timedelta(seconds=elapsed_time))
