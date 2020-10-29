# Data collection program for cs425 final project
# Author: Tristen Finley (tfinley3)

#WARNING: Program can take a very long time to run if you are asking for more than 1 or 2 posts, because
#the api can only grab 100 comments at a time and some have up to 3k comments (30 api calls) and api is slower than christmas
import requests
from datetime import datetime
import time
import csv
    
subs = ['gatesopencomeonin', 'gatekeeping'] #list of subs to pull from (large subs take forever)
posts = 1 #how many posts we gather for each sub, sorted by most upvotes (top posts)
size = 100
if posts < 100:
    size = posts
submissiondata = []
commentdata = []

#list for or word checks
nice_words = ['nice', 'good', 'okay', 'too', 'valid', 'like', 'wholesome']
bad_words = ['cant', 'cant', 'wont', 'fuck', 'shit', 'cuck']
general_words = ['all', 'any', 'every']

percent_deleted = []
avg_comment_karma = []
total_post_karma = []
comment_upvote_rate = []
nice_words_per_comment = []
negative_words_per_comment = []
general_words_per_comment = []
comments_per_min = []
karma_per_min = []
avg_comment_words = []
avg_word_len = []
target_label = []
post_id = []

posturl = "https://api.pushshift.io/reddit/submission/search/?subreddit={}&sort_type=score&size={}&score=<"
commenturl = "https://api.pushshift.io/reddit/comment/search/?subreddit={}&size=1000&link_id={}&before="
start_time = datetime.utcnow()

#gather data
for subreddit in subs:
    score = 1000000
    num_posts = 0
    while(num_posts < posts):
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
        num_posts += len(dat)
        submissiondata.extend(dat)
        score = dat[-1]['score']

i=0
for post in submissiondata:
    prev_epoch = int(start_time.timestamp())
    comments = []
    while True:
        new_url = commenturl.format(post['subreddit'], post['id']) + str(prev_epoch)
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
    commentdata.append(comments)
    print(len(commentdata[i]))
    i += 1

#filter data into features
i = 0
for post in submissiondata:
    comments = commentdata[i]
    i += 1
    ND = 0
    NW = 0
    NB = 0
    NG = 0
    karma = 0
    words = 0
    avg_len = 0
    first_utc = post['created_utc']
    last_utc = 0
    for comment in comments:
        if(comment['created_utc'] > last_utc):
            last_utc = comment['created_utc']
        if(comment['author'] == '[removed]' or comment['author'] == '[deleted]'):
            ND += 1
        karma += comment['score']
        word_len = 0
        
        #remove punctuation so it doesnt interfere with word counts
        comment['body'] = comment['body'].replace('\'', '')
        comment['body'] = comment['body'].replace('.', '')
        comment['body'] = comment['body'].replace('!', '')
        comment['body'] = comment['body'].replace('?', '')
        
        for word in comment['body'].split():
            if(word in nice_words):
                NW += 1
            elif(word in bad_words):
                NB += 1
            elif(word in general_words):
                NG += 1
            word_len += len(word)
            words += 1
        avg_len += word_len / len(word)
    
    avg_len /= len(comments)
    total_utc = last_utc - first_utc

    percent_deleted.append(ND / len(comments))
    avg_comment_karma.append(karma / len(comments))
    total_post_karma.append(post['score'])
    comment_upvote_rate.append(post['score'] / len(comments))
    nice_words_per_comment.append(NW / len(comments))
    negative_words_per_comment.append(NB / len(comments))
    general_words_per_comment.append(NG / len(comments))
    avg_comment_words.append(words / len(comments))
    comments_per_min.append(len(comments) / (total_utc/60))
    karma_per_min.append(post['score'] / (total_utc/60))
    avg_word_len.append(avg_len)
    target_label.append(post['subreddit'])
    post_id.append(post['id'])
    
#write features to csv file
with open('postdata.csv', 'w', newline = '') as f:
    fieldnames = ['% deleted comments',
                  'avg comment karma',
                  'total post karma',
                  'comment to karma rate',
                  'nice words per comment',
                  'negative words per comment' ,
                  'general words per comment',
                  'avg words per comment',
                  'avg word len',
                  'comments per min',
                  'karma per min',
                  'sub',
                  'post id']
    write = csv.DictWriter(f, fieldnames = fieldnames)
    write.writeheader()

    i = 0
    for post in submissiondata:
        write.writerow({'% deleted comments' : percent_deleted[i],
                       'avg comment karma' : avg_comment_karma[i],
                       'total post karma' : total_post_karma[i],
                       'comment to karma rate' : comment_upvote_rate[i],
                       'nice words per comment' : nice_words_per_comment[i],
                       'negative words per comment' : negative_words_per_comment[i],
                       'general words per comment' : general_words_per_comment[i],
                       'avg words per comment' : avg_comment_words[i],
                       'avg word len' : avg_word_len[i],
                       'comments per min' : comments_per_min[i],
                       'karma per min' : karma_per_min[i],
                        'sub' : target_label[i],
                        'post id' : post_id[i]})
        i += 1
