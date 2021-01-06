import os
import requests
import tweepy
from datetime import datetime, date

# API Key : JjSSCoFSbnQh97VDe95DBYEQd
# API Secret Key : 3ssHOGHiO51BrrNS09IzGt95Y0ZY5kn1cvDX3DOJ7fcWlfafTK
# Bearer Token : AAAAAAAAAAAAAAAAAAAAAA7HKwEAAAAACsInzc4PXhy2CjC2i60LzcYYqTM%3DdSFDDZMPARdxItZbgTXeyKrp8RLnHQeWg4tFlnTRKLJq4JjVqy
# Access Token : 1341018559976255491-3RODUajAoWdgEqNMBQuLnqutfh4va8
# Access Token Secret : CisUExnCCq5CTQ5XUWuLYIt3NCn36rgrjsfYio6TtPSMk

class Twitter_Scraper():
    def __init__(self, keyword_or_userid, image_number):
        self.keyword_or_userid = keyword_or_userid
        self.image_number = image_number

        self.since = None
        self.until = None
        # ask user if they want to download posts in certain time period
        print("Download posts in certain time period?\n(1) Yes\n(2) No")
        option = input("Enter (1) or (2): ")
        print("")

        # if user wants to download in certain time period, ask the user the dates
        # if the user doesnt want to download posts in certain time, just download normally
        if option == '1':
            since_year = int(input("Since year: "))
            since_month = int(input("Since month: "))
            since_day = int(input("Since day: "))
            until_year = int(input("Until year: "))
            until_month = int(input("Until month: "))
            until_day = int(input("Until day: "))
            print("")
            self.since = datetime(since_year, since_month, since_day)
            self.until = datetime(until_year, until_month, until_day)

        #setting up the the twitter API
        auth = tweepy.OAuthHandler("JjSSCoFSbnQh97VDe95DBYEQd", "3ssHOGHiO51BrrNS09IzGt95Y0ZY5kn1cvDX3DOJ7fcWlfafTK")
        auth.set_access_token("1341018559976255491-3RODUajAoWdgEqNMBQuLnqutfh4va8",
                              "CisUExnCCq5CTQ5XUWuLYIt3NCn36rgrjsfYio6TtPSMk")
        self.api = tweepy.API(auth)


    #this function search for tweets based on a keyword and downloads their contents
    def download_tweets_from_keyword(self, keyword_path, media_path):
        tweet_counter = 0
        tweets = tweepy.Cursor(self.api.search,q=self.keyword_or_userid+" -filter:retweets").items()
        for tweet in tweets:
            if tweet_counter == self.image_number:
                break

            if self.since is not None and self.until is not None:
                if not (tweet.created_at > self.since and tweet.created_at < self.until):
                    continue

            # specify the file name and path. if the tweet was already scraped, ignore it
            #the file is named according to the tweet id and today's date
            file_name = tweet.id_str + "_" + str(date.today()) + ".txt"
            file_path = os.path.join(keyword_path, file_name)
            if os.path.isfile(file_path):
                continue

            #try writing the text to the file. sometimes it doesnt work because the text is in foreign format,
            #therefore this code handles it by deleting the empty txt file
            try:
                with open(file_path, 'w') as f:
                    f.write(tweet.text
                            + "\nLikes: " + str(tweet.favorite_count)
                            + "\nUser: @" + str(tweet.user.screen_name)
                            + "\nPosted at: " + str(tweet.created_at))
            except Exception as e:
                os.remove(file_path)
                continue

            if 'media' in tweet.entities:
                #a tweet can consist of up to 4 images. the name of the image is tweet_id + image_index
                image_index = 0
                for media in tweet.extended_entities['media']:
                    image = requests.get(media['media_url_https'])
                    if 200 == image.status_code:
                        image_name = tweet.id_str + "_" + str(image_index) + ".jpg"
                        image_path = os.path.join(media_path, image_name)
                        try:
                            with open(image_path, 'wb') as f:
                                f.write(image.content)
                        except Exception as e:
                            continue
                    image_index += 1
            tweet_counter += 1


    # this function get tweets from a certain user. make sure to include in classes.txt the username, for example
    # @billieeilish (with the @), as twitter username is unique, and NOT the display name
    def download_tweets_from_user(self, keyword_path, media_path):
        tweet_counter = 0
        for tweet in tweepy.Cursor(self.api.user_timeline,
                                   screen_name=self.keyword_or_userid,
                                   include_rts=False,
                                   tweet_mode='extended').items():
            if tweet_counter == self.image_number:
                break

            if self.since is not None and self.until is not None:
                if not (tweet.created_at > self.since and tweet.created_at < self.until):
                    continue

            # specify the file name and path. if the tweet was already scraped, ignore it
            #the file is named according to the tweet id and today's date
            file_name = tweet.id_str + "_" + str(date.today()) + ".txt"
            file_path = os.path.join(keyword_path, file_name)
            if os.path.isfile(file_path):
                continue

            # try writing the text to the file. sometimes it doesnt work because the text is in foreign format,
            # therefore this code handles it by deleting the empty txt file
            try:
                with open(file_path, 'w') as f:
                    f.write(tweet.full_text
                            + "\nLikes: " + str(tweet.favorite_count)
                            + "\nPosted at: " + str(tweet.created_at))
            except Exception as e:
                os.remove(file_path)
                continue

            if 'media' in tweet.entities:
                # a tweet can consist of up to 4 images. the name of the image is tweet_id + image_index
                image_index = 0
                for media in tweet.extended_entities['media']:
                    image = requests.get(media['media_url_https'])
                    if 200 == image.status_code:
                        image_name = tweet.id_str + "_" + str(image_index) + ".jpg"
                        image_path = os.path.join(media_path, image_name)
                        try:
                            with open(image_path, 'wb') as f:
                                f.write(image.content)
                        except Exception as e:
                            continue
                    image_index += 1

            tweet_counter += 1


    def twitter_scraper(self):
        #ask the user if they wants to download based on keywords or download tweets from users
        print("(1) Download tweets based on keyword(s)\n(2) Download tweets from user(s)")
        choice = input("Enter 1 or 2: ")

        cwd = os.getcwd()
        #split the folders to keywords and users
        if choice == '1':
            if not os.path.isdir("{}/database/twitter/keywords/{}/media".format(cwd, self.keyword_or_userid)):
                os.makedirs("{}/database/twitter/keywords/{}/media".format(cwd, self.keyword_or_userid))
            keyword_path = "{}/database/twitter/keywords/{}".format(cwd, self.keyword_or_userid)
            media_path = "{}/database/twitter/keywords/{}/media".format(cwd, self.keyword_or_userid)
            self.download_tweets_from_keyword(keyword_path, media_path)
        elif choice == '2':
            if not os.path.isdir("{}/database/twitter/users/{}/media".format(cwd, self.keyword_or_userid)):
                os.makedirs("{}/database/twitter/users/{}/media".format(cwd, self.keyword_or_userid))
            keyword_path = "{}/database/twitter/users/{}".format(cwd, self.keyword_or_userid)
            media_path = "{}/database/twitter/users/{}/media".format(cwd, self.keyword_or_userid)
            self.download_tweets_from_user(keyword_path, media_path)
