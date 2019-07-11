#from __future__ import unicode_literals
import twitter_credentials as cred
import tweepy
import pickle
import os
import datetime
import time
import re
import boto
from os import listdir 
from os.path import isfile, join 
import pandas as pd

class read_tweets(object):
    
    def __init__(self):
        self.auth = tweepy.OAuthHandler(cred.consumer_key, cred.consumer_secret)
        self.auth.set_access_token(cred.access_token, cred.access_token_secret)
        self.api = tweepy.API(self.auth)
        self.df_emoji = pd.read_pickle('./data/df_emoji.pkl')

    def get_tweets(self, topic, save_file_name, num_batches = 10, num_tweets = 20, to_bucket = False): 
        # num_batches * num_tweets is total tweets target
        tweets = set()
        # public_tweets = api.home_timeline()
        for i in range(num_batches):
            try:
                print('Loading', i+1, 'of', num_batches)
                for tweet in tweepy.Cursor(self.api.search, q=topic).items(num_tweets): #100 batches of 20

                    if tweet.lang == 'en':
                        tweets.add(tweet.text) 

                time.sleep(35) 
            except:
                print('Waiting for API to allow more calls...')
                time.sleep(60)
                pass

        # if to_bucket:
            pass
        else:
            pickle.dump(tweets, open( "{}.pkl".format(save_file_name), "wb" ) )
            print('Succesfully pickled', len(tweets), 'tweets!')
            
        return(tweets)
    
    def keyword_tweets(self, keywords, num_batches = 10, num_tweets = 20):
        
        now = datetime.datetime.today().ctime()
        now = re.sub(' ','_',now)
        now = re.sub(':','-',now)


        # use boto to connect to aws buckets
        conn = boto.connect_s3(cred.aws_access_key, cred.aws_access_secret_key)

        # what bucket?
        bucket_name = 'emoji-tweets'

        # check if bucket exists if not make it
        if conn.lookup(bucket_name) is None:
            b = conn.create_bucket(bucket_name)
        else:
            b = conn.get_bucket(bucket_name)

        #some simple english words
        #words = ['is', 'it', 'the']
        words = []
        words.extend(keywords)
        
        tweets = []

        for word in words:
            pkl_name = './tweet_data/tweets_{}_{}'.format(now,word)
            s3_name = 'tweets_{}_{}.pkl'.format(now,word)
            loc_name = './tweet_data/tweets_{}_{}.pkl'.format(now,word)
            tweets += self.get_tweets(word, pkl_name, num_batches = num_batches, num_tweets = num_tweets)

            # save the pkl file
            file_object = b.new_key(s3_name)#where to save
            file_object.set_contents_from_filename(loc_name)

            print('Successfully saved {} to S3 bucket {}'.format(s3_name,bucket_name))
        # to read the file
        #fil_object.get_contents_to_file('folder/file')        
        return(tweets)
    
    def all_tweets(self, keywords, num_batches = 10, num_tweets = 20):
        '''
        run keyword_tweets() and 
        combinine with the tweets that is already read and are in tweet_data folder
        '''
        mypath = './tweet_data'
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        
        tweets = self.keyword_tweets(keywords, num_batches = num_batches, num_tweets = num_tweets)
        for i in files:
            if i != '.DS_Store':
                file = './tweet_data/'+ i
                tweets += list(pickle.load(open(file,'rb')))
        
        # removing duplicates
        tweets = list(dict.fromkeys(tweets))
        return(tweets)

    def emoji_tweets(self, keywords, num_batches = 10, num_tweets = 20):
        '''
        finding the tweets with emojis
        ''' 
        tweets = self.all_tweets(keywords, num_batches = num_batches, num_tweets = num_tweets)
        no_moji = []
        yay_moji = []
        for tweet in tweets:
            tweet = str(tweet) #some have type tweepy.models.Status
            yay = False
            for uni in self.df_emoji['unichar']:
                #if emoji in str(tweet):
                if uni in tweet:
                    yay = True
            if yay:
                yay_moji.append(tweet)
            else: # else statement to create no_moji list
                no_moji.append(tweet)
        
        pickle.dump(yay_moji, open( "./data/yay_moji.pkl", "wb"))
        print('Succesfully pickled {} tweets and emoji data frame'.format(len(yay_moji)))
        
        return(yay_moji)