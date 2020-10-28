import requests
from datetime import datetime
import time

subs = ['lemonjelly'] #list of subs to pull from (large subs take forever)
day = '1' #how many days back we look
url = "https://api.pushshift.io/reddit/{}/search/?subreddit={}&size=100&sort=desc&after={}d&before="
object_type = ["submission", "comment"]
start_time = datetime.utcnow()

for subreddit in subs:

    nlocked=0
    nremoved=0
    submissiondata = []
    commentdata = []
    for s in object_type:
        prev_epoch = int(start_time.timestamp())
        while True:
            time.sleep(1) #have to wait inbetween api calls so there is no errors
            new_url = url.format(s, subreddit, day)+str(prev_epoch)
            res = requests.get(new_url)
            print(new_url)
            try:
                dat = res.json()['data']
            except ValueError:
                print("API Error, trying again")
                continue
            if(len(dat) == 0):
                break
            if(s == 'comment'):
                commentdata.extend(dat)
            elif(s == 'submission'):
                submissiondata.extend(dat)
            prev_epoch=dat[-1]['created_utc']

    for post in submissiondata:
        if(post['locked'] == True):
            nlocked+=1;

    for comment in commentdata:
        if(comment['author'] == 'removed'):
            nremoved += 1

    print("Number of locked posts: {}".format(nlocked))
    print("Number of removed comments: {}".format(nremoved))

print(len(submissiondata))
print(len(commentdata))
