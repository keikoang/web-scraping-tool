import os
import requests
from TwitterSearch import *


# API Key : JjSSCoFSbnQh97VDe95DBYEQd
# API Secret Key : 3ssHOGHiO51BrrNS09IzGt95Y0ZY5kn1cvDX3DOJ7fcWlfafTK
# Bearer Token : AAAAAAAAAAAAAAAAAAAAAA7HKwEAAAAACsInzc4PXhy2CjC2i60LzcYYqTM%3DdSFDDZMPARdxItZbgTXeyKrp8RLnHQeWg4tFlnTRKLJq4JjVqy
# Access Token : 1341018559976255491-3RODUajAoWdgEqNMBQuLnqutfh4va8
# Access Token Secret : CisUExnCCq5CTQ5XUWuLYIt3NCn36rgrjsfYio6TtPSMk

class Twitter_Scraper():
    def __init__(self, keyword, image_number):
        self.keyword = keyword
        self.image_number = image_number

        cwd = os.getcwd()
        if not os.path.isdir("{}/database/twitter/{}".format(cwd, self.keyword)):
            os.makedirs("{}/database/twitter".format(cwd, self.keyword))
        self.twitter_path = "{}/database/twitter/{}".format(cwd, self.keyword)

        if not os.path.isdir("{}/database/twitter/{}/media".format(cwd, self.keyword)):
            os.makedirs("{}/database/twitter/{}/media".format(cwd, self.keyword))
        self.media_folder = "{}/database/twitter/{}/media".format(cwd, self.keyword)

    def twitter_scraper(self):
        tweet_counter = 0
        try:
            tso = TwitterSearchOrder()
            keyword_list = [self.keyword]
            tso.set_keywords(keyword_list)

            ts = TwitterSearch(
                consumer_key='JjSSCoFSbnQh97VDe95DBYEQd',
                consumer_secret='3ssHOGHiO51BrrNS09IzGt95Y0ZY5kn1cvDX3DOJ7fcWlfafTK',
                access_token='1341018559976255491-3RODUajAoWdgEqNMBQuLnqutfh4va8',
                access_token_secret='CisUExnCCq5CTQ5XUWuLYIt3NCn36rgrjsfYio6TtPSMk'
            )

            for tweet in ts.search_tweets_iterable(tso):
                if tweet_counter == self.image_number:
                    break

                file_name = tweet['id_str'] + '.txt'
                file_path = os.path.join(self.twitter_path, file_name)
                # if the tweet was already scraped, ignore it
                if os.path.isfile(file_path):
                    continue
                # write the tweet text to a txt file
                try:
                    with open(file_path, 'w') as f:
                        f.write(tweet['text'])
                except Exception as e:
                    os.remove(file_path)
                    continue

                # if the list is not empty
                if 'media' in tweet['entities']:
                    medias = tweet['entities']['media']
                    for media in medias:
                        print(media['type'])
                        if media['type'] == 'photo':
                            image = requests.get(media['media_url_https'])
                            if 200 == image.status_code:
                                image_name = tweet['id_str'] + '.jpg'
                                image_path = os.path.join(self.media_folder, image_name)
                                with open(image_path, 'wb') as f:
                                    f.write(image.content)
                tweet_counter += 1
        except TwitterSearchException as e:
            print(e)