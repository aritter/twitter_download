import sys
import os
import time
import datetime

from twitter import *

CONSUMER_KEY='JEdRRoDsfwzCtupkir4ivQ'
CONSUMER_SECRET='PAbSSmzQxbcnkYYH2vQpKVSq2yPARfKm0Yl6DrLc'

MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
if not os.path.exists(MY_TWITTER_CREDS):
    oauth_dance("Semeval sentiment analysis", CONSUMER_KEY, CONSUMER_SECRET, MY_TWITTER_CREDS)
oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

cache = {}

for line in open(sys.argv[1]):
    fields = line.strip().split('\t')
    sid = fields[0]
    uid = fields[1]

    while not cache.has_key(sid):
        try:
            text = t.statuses.show(_id=sid)['text'].replace('\n', ' ').replace('\r', ' ')
            cache[sid] = text
        except TwitterError as e:
            if e.e.code == 429:
                rate = t.application.rate_limit_status()
                reset = rate['resources']['statuses']['/statuses/show/:id']['reset']
                now = datetime.datetime.today()
                future = datetime.datetime.fromtimestamp(reset)
                sys.stderr.write("Rate limit exceeded, sleeping until %s\n" % future)
                time.sleep((future-now).seconds)
            else:
                cache[sid] = 'Not Available'
            
    text = cache[sid]

    print "\t".join(fields + [text])
