from instaloader import Instaloader, Post, Profile
from instaloader.__main__ import filterstr_to_filterfunc
from instaloader.instaloader import _ArbitraryItemFormatter, _PostPathFormatter
import os
import time
from itertools import dropwhile, takewhile
from datetime import datetime


class Instagram_Scraper():
    def __init__(self, hashtags_or_users, image_number):
        self.hashtags_or_users = hashtags_or_users
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

        # make the directory for instagram if they dont exist
        cwd = os.getcwd()
        if not os.path.isdir("{}/database/instagram".format(cwd)):
            os.makedirs("{}/database/instagram".format(cwd))


    # this function get posts with one hashtag and download the contents + captions
    def download_post_with_one_hashtag(self, loader, hashtag):
        count = 0
        #set the directory name the same as the hashtag
        loader.dirname_pattern = "database/instagram/hashtags/{}".format(hashtag)
        caption_folder = "database/instagram/hashtags/{}/captions".format(hashtag)

        posts = loader.get_hashtag_posts(hashtag)
        if self.since is not None and self.until is not None:
            posts = takewhile(lambda p: p.date > self.since, dropwhile(lambda p: p.date > self.until, posts))

        print("\n--- Downloading post(s) with {} hashtag ---".format(hashtag))
        for post in posts:
            if count > self.image_number - 1:
                break
            #if only download videos
            if (not loader.download_pictures) and loader.download_videos:
                if not post.is_video:
                    continue

            downloaded = loader.download_post(post, hashtag)
            if downloaded:  # if the post is succesfully downloaded, download the caption
                metadata_string = _ArbitraryItemFormatter(post).format('{caption}').strip()
                dirname = _PostPathFormatter(post).format(caption_folder, hashtag)
                filename = os.path.join(dirname, loader.format_filename(post, hashtag))
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                loader.save_caption(filename=filename, mtime=post.date_local, caption=metadata_string)
                count += 1
            time.sleep(1)  # give some time to minimize getting banned from instagram


    # this function get posts that contains both hashtag X AND hashtag Y, download the contents + captions
    def download_post_with_two_hashtag(self, loader, two_hashtags):
        i = 0
        count = 0
        # this code block handles keywords with space
        while i < 2:
            if " " in two_hashtags[i]:
                two_hashtags[i] = "".join(two_hashtags[i].split())
            i += 1

        #glue the two hashtags together and set the directory name the same as joined hashtag
        joined_hashtags = '_'.join(two_hashtags)
        loader.dirname_pattern = "database/instagram/hashtags/{}".format(joined_hashtags)
        caption_folder = "database/instagram/hashtags/{}/captions".format(joined_hashtags)
        #set the second hashtag as the filter
        filter = filterstr_to_filterfunc("'{}' in caption_hashtags".format(two_hashtags[1]), Post)

        posts = loader.get_hashtag_posts(two_hashtags[0])
        if self.since is not None and self.until is not None:
            posts = takewhile(lambda p: p.date > self.since, dropwhile(lambda p: p.date > self.until, posts))

        print("\n--- Downloading post(s) with {} hashtags ---".format(', '.join(two_hashtags)))
        for post in posts:
            if count > self.image_number - 1:
                break
            # if only download videos
            if (not loader.download_pictures) and loader.download_videos:
                if not post.is_video:
                    continue
            if filter(post):
                downloaded = loader.download_post(post, joined_hashtags)
                if downloaded:  # if the post is succesfully downloaded, download the caption
                    metadata_string = _ArbitraryItemFormatter(post).format('{caption}').strip()
                    dirname = _PostPathFormatter(post).format(caption_folder, joined_hashtags)
                    filename = os.path.join(dirname, loader.format_filename(post, joined_hashtags))
                    os.makedirs(os.path.dirname(filename), exist_ok=True)
                    loader.save_caption(filename=filename, mtime=post.date_local, caption=metadata_string)
                    count += 1
            time.sleep(1)


    # this function get posts from certain username, and
    def download_post_from_user(self, loader, user):
        count = 0
        # set the directory name the same as the hashtag
        loader.dirname_pattern = "database/instagram/users/{}".format(user)
        caption_folder = "database/instagram/users/{}/captions".format(user)
        profile = Profile.from_username(loader.context, user)
        posts = profile.get_posts()

        if self.since is not None and self.until is not None:
            posts = takewhile(lambda p: p.date > self.since, dropwhile(lambda p: p.date > self.until, posts))

        print("\n--- Downloading post(s) from user {} ---".format(user))
        for post in posts:
            if count > self.image_number - 1:
                break

            #if only download videos
            if (not loader.download_pictures) and loader.download_videos:
                if not post.is_video:
                    continue
            downloaded = loader.download_post(post, target=profile.username)
            if downloaded:  # if the post is succesfully downloaded, download the caption
                metadata_string = _ArbitraryItemFormatter(post).format('{caption}').strip()
                dirname = _PostPathFormatter(post).format(caption_folder, user)
                filename = os.path.join(dirname, loader.format_filename(post, user))
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                loader.save_caption(filename=filename, mtime=post.date_local, caption=metadata_string)
                count += 1
            time.sleep(1)  # give some time to minimize getting banned from instagram


    def instagram_scraper(self):
        print("(1) Download posts based on hashtag(s)\n(2) Download posts from user(s)")
        choice = input("Enter 1 or 2: ")
        print("")

        print("(1) Image only\n(2) Video only\n(3) Both Image and video")
        download_option = input("Enter 1, 2, or 3: ")
        print("")

        # initialize the instaloader instance
        loader = None
        if download_option == '1':
            loader = Instaloader(
                sleep=True, quiet=False, filename_pattern='{profile}_{date}', download_pictures=True,
                download_videos=False, download_video_thumbnails=True, download_geotags=False,
                download_comments=False, save_metadata=False, post_metadata_txt_pattern='')
        elif download_option == '2':
            loader = Instaloader(
                sleep=True, quiet=False, filename_pattern='{profile}_{date}', download_pictures=False,
                download_videos=True, download_video_thumbnails=False, download_geotags=False,
                download_comments=False, save_metadata=False, post_metadata_txt_pattern='')
        elif download_option == '3':
            loader = Instaloader(
                sleep=True, quiet=False, filename_pattern='{profile}_{date}', download_pictures=True,
                download_videos=True, download_video_thumbnails=False, download_geotags=False,
                download_comments=False, save_metadata=False, post_metadata_txt_pattern='')

        # login to a premade account to minimize chance of getting banned from instagram
        loader.login(user='webscrapingtool.rug', passwd='w3bscr4p1ng')

        if choice == '1':
            print("(1) Download with one hashtag\n(2) Download with two hashtag")
            hashtag_option = input("Enter 1 or 2: ")
            print("")
            if hashtag_option == '1':
                for hashtag in self.hashtags_or_users:
                    parsed_hashtag = hashtag
                    if " " in hashtag:
                        parsed_hashtag = "".join(hashtag.split())
                    try:
                        self.download_post_with_one_hashtag(loader, parsed_hashtag)
                    except Exception as e:
                        pass
                    time.sleep(3)  # to prevent request overload
            elif hashtag_option == '2':
                try:
                    self.download_post_with_two_hashtag(loader, self.hashtags_or_users)
                except Exception as e:
                    pass
        elif choice == '2':
            for user in self.hashtags_or_users:
                self.download_post_from_user(loader, user)
