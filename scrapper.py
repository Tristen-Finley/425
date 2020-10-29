import requests
from datetime import datetime
import time
    
subs = ['gatesopencomeonin','gatekeeping'] #list of subs to pull from (large subs take forever)
posts = 10 #how many posts we gather, sorted by moist upvotes
size = 100
if posts < 100:
    size = posts

posturl = "https://api.pushshift.io/reddit/submission/search/?subreddit={}&sort_type=score&size={}&score=<"
commenturl = "https://api.pushshift.io/reddit/comment/search/?subreddit={}&size=100&link_id={}&before="
start_time = datetime.utcnow()

for subreddit in subs:

    submissiondata = []
    comments = []
    commentdata = []
    request_type = 'submission'
    score = 1000000
    while(len(submissiondata) < posts):
        new_url = posturl.format(subreddit,size)+str(score)
        res = requests.get(new_url)
        print(new_url)
        try:
            dat = res.json()['data']
        except ValueError:
            print("API Error, trying again")
            continue
        if(len(dat) == 0):
            break
        submissiondata.extend(dat)
        score = dat[-1]['score']

    for post in submissiondata:
        prev_epoch = int(start_time.timestamp())
        while True:
            new_url = commenturl.format(subreddit, post['id']) + str(prev_epoch)
            res = requests.get(new_url)
            print(new_url)
            try:
                dat = res.json()['data']
            except ValueError:
                print("API Error, trying again")
                continue
            if(len(dat) == 0):
               break
            comments.extend(dat)
            prev_epoch = dat[-1]['created_utc']
        commentdata.extend(comments)
        
    print(len(submissiondata))
    print(len(commentdata))

    for comments in commentdata:
        print(len(comments))


