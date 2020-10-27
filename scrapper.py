import requests
from datetime import datetime
import time

subs = ['lemonjelly'] #list of subs to pull from (large subs take forever)
day = '30' #how many days back we look
url = "https://api.pushshift.io/reddit/{}/search/?subreddit={}&limit=1000&sort=desc&after={}d&before="
object_type = ["submission", "comment"]
start_time = datetime.utcnow()

for subreddit in subs:
    
    count = 0
    prev_epoch = int(start_time.timestamp())
    submissiondata = []
    commentdata = []
    for s in object_type:
        while True:
            new_url = url.format(s, subreddit, day)+str(prev_epoch)
            res = requests.get(new_url)
            print(new_url)
            dat = res.json()['data']
            if(len(dat) == 0):
                break
            if(s == 'comment'):
                commentdata.extend(dat)
            elif(s == 'submission'):
                submissiondata.extend(dat)
            prev_epoch=dat[-1]['created_utc']
    
print(len(submissiondata))
print(len(commentdata))
