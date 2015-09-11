import sys
import os
import time
import datetime
import argparse

from twitter import *

parser = argparse.ArgumentParser(description="downloads tweets")
parser.add_argument('--partial', dest='partial', default=None, type=argparse.FileType('r'))
parser.add_argument('--dist', dest='dist', default=None, type=argparse.FileType('r'), required=True)
parser.add_argument('--output', dest='output', default=None, type=argparse.FileType('w'), required=True)

args = parser.parse_args()

CONSUMER_KEY='JEdRRoDsfwzCtupkir4ivQ'
CONSUMER_SECRET='PAbSSmzQxbcnkYYH2vQpKVSq2yPARfKm0Yl6DrLc'

MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
if not os.path.exists(MY_TWITTER_CREDS):
    oauth_dance("Semeval sentiment analysis", CONSUMER_KEY, CONSUMER_SECRET, MY_TWITTER_CREDS)
oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

cache = {}
if args.partial != None:
    for line in args.partial:
        fields = line.strip().split("\t")
        text = fields[-1]
        sid = fields[0]
        cache[sid] = text

for line in args.dist:
    fields = line.strip().split('\t')
    sid = fields[0]
    uid = fields[1]

    while not sid in cache:
        try:
            text = t.statuses.show(_id=sid)['text'].replace('\n', ' ').replace('\r', ' ')
            cache[sid] = text
        except TwitterError as e:
            if e.e.code == 429:
                rate = t.application.rate_limit_status()
                reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                now = datetime.datetime.today()
                future = datetime.datetime.fromtimestamp(reset)
                seconds = (future-now).seconds+1
                if seconds < 10000:
                    sys.stderr.write("Rate limit exceeded, sleeping for %s seconds until %s\n" % (seconds, future))
                    time.sleep(seconds)
            else:
                cache[sid] = 'Not Available'

    text = cache[sid]

    args.output.write("\t".join(fields + [text]) + '\n')
