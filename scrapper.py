# Data collection program for cs425 final project
# Author: Tristen Finley (tfinley3)

#WARNING: Program can take a very long time to run if you are asking for more than 1 or 2 posts, because
#the api can only grab 100 comments at a time and some have up to 3k comments (30 api calls) and api is slower than christmas

import requests
import datetime
import time
import csv
import praw
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from praw.exceptions import APIException

analyzer = SentimentIntensityAnalyzer()

subs = ['gatesopencomeonin', 'gatekeeping'] #list of subs to pull from (large subs take forever)

reddit = praw.Reddit(client_id = 'KQV6cD-fb7Je-A',
                     client_secret = 'ew7VIiDOhKMzwPIdDGzz6Gf30MU',
                     username = 'ColdMF',
                     user_agent = 'scrapper for mahcine learning by /u/ColdMF',
                     )

# feature lists
percent_deleted = []
avg_comment_karma = []
total_post_karma = []
comment_upvote_rate = []
comments_per_min = []
karma_per_min = []
avg_comment_words = []
allpostcomments = []
avg_word_len = []
target_label = []
avg_vader_sentiment = []
post_id = []
#relevant words found from wordcloud generator : https://sandhoefner.github.io/reddit/
contains_cant = []
contains_dont = []
contains_everyone = []
contains_anyone = []
contains_happy = []
contains_love = []

for sub in subs:
    subreddit = reddit.subreddit(sub)
    p = { "t" : "year" }
    posts = subreddit.top(limit = 500, params = p)
    i = 0
    for post in posts:
        score = post.score
        num_comments = 0
        sentiment = 0
        comment_karma = 0
        num_deleted = 0
        post_creation = post.created
        last_comment = 0
        n_isnt = 0
        n_cant = 0
        n_dont = 0
        n_everyone = 0
        n_anyone = 0
        n_wholesome = 0
        n_happy = 0
        n_love = 0
        num_words = 0
        num_characters = 0
        
        #error handler for API calls
        while True:
            try:
                post.comments.replace_more(limit=None, threshold=0)
                break
            except APIException as e:
                print("Handling replace_more exception")
                sleep(1)

        #some deleted commetns arent archived quickly enough to be stored in API listing,
        #we are only ocunting what we can find, except for num_deleted which is a metric
        #we must measure with full accuracy
        num_deleted = abs(post.num_comments - len(post.comments.list()))
        num_comments = len(post.comments.list())
        archived_deleted = 0
        
        for comment in post.comments.list():

            #last comment time used to claculate the total time the post is "active"
            if(comment.created > last_comment):
                last_comment = comment.created

            comment_karma += comment.score

            if(comment.body == "[removed]" or comment.body == "[deleted]" or comment.body == None):
                num_deleted += 1
                archived_deleted += 1
                continue

            sentiment_dict = analyzer.polarity_scores(comment.body)
            sentiment += sentiment_dict['compound']
            
            #sanitize text for easier parsing
            comment.body = comment.body.replace('\'', '')
            comment.body = comment.body.replace('/', '')
            comment.body = comment.body.replace('\\', '')
            comment.body = comment.body.replace('.', '')
            comment.body = comment.body.replace('!', '')
            comment.body = comment.body.replace('?', '')
            comment.body = comment.body.replace('"', '')
            comment.body.lower()

            for word in comment.body.split():
                num_words += 1
                num_characters += len(word)
                if(word == 'cant'):
                    n_cant += 1
                if(word == 'dont'):
                    n_dont += 1
                if(word == 'everyone'):
                    n_everyone += 1
                if(word == 'anyone'):
                    n_anyone += 1
                if(word == 'happy'):
                    n_happy += 1
                if(word == 'love'):
                    n_love += 1

        #claculating / appending features
        percent_deleted.append(num_deleted / post.num_comments)
        avg_comment_karma.append(comment_karma / num_comments)
        total_post_karma.append(score)
        comment_upvote_rate.append(score / num_comments)
        comments_per_min.append(num_comments / ((last_comment - post_creation) / 60))
        karma_per_min.append(score / ((last_comment - post_creation) / 60))
        post_id.append(post.id)
        target_label.append(post.subreddit)
        
        #dont count deleted comments in archive since they have no text
        num_comments -= archived_deleted
        
        contains_cant.append(n_cant / num_comments)
        contains_dont.append(n_dont / num_comments)
        contains_everyone.append(n_everyone / num_comments)
        contains_anyone.append(n_anyone / num_comments)
        contains_happy.append(n_happy / num_comments)
        contains_love.append(n_love / num_comments)
        avg_comment_words.append(num_words / num_comments)
        avg_word_len.append(num_characters / num_words)
        avg_vader_sentiment.append(sentiment / num_comments)
              
        i += 1
        print(i)
        print()
            

#write features to csv file
with open('postdata.csv', 'w', newline = '') as f:
    fieldnames = ['Percdeleted',
                  'AvgComKarma',
                  'TotalKarma',
                  'ComUpRatio',
                  'ContainsCant',
                  'ContainsDont',
                  'ContainsEveryone',
                  'ContainsAnyone',
                  'ContainsHappy',
                  'ContainsLove',
                  'AvgComLen',
                  'AvgWordLen',
                  'AvgCommTime',
                  'VoteTime',
                  'AvgVaderSentiment',
                  'post id',
                  'sub']
    write = csv.DictWriter(f, fieldnames = fieldnames)
    write.writeheader()

    i = 0
    for post in post_id:
        write.writerow({'Percdeleted' :percent_deleted[i],
                    'AvgComKarma' : avg_comment_karma[i],
                    'TotalKarma' : total_post_karma[i],
                    'ComUpRatio' :comment_upvote_rate[i],
                    'ContainsCant' : contains_cant[i],
                    'ContainsDont' : contains_dont[i],
                    'ContainsEveryone' : contains_everyone[i],
                    'ContainsAnyone' : contains_anyone[i],
                    'ContainsHappy' : contains_happy[i],
                    'ContainsLove' : contains_love[i],
                    'AvgComLen' : avg_comment_words[i],
                    'AvgWordLen' : avg_word_len[i],
                    'AvgCommTime' : comments_per_min[i],
                    'VoteTime' : karma_per_min[i],
                    'AvgVaderSentiment' : avg_vader_sentiment[i], 
                    'post id' : post_id[i],
                    'sub' : target_label[i]})
        i += 1
