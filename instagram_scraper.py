from instaloader import Instaloader, Post
from instaloader.__main__ import filterstr_to_filterfunc
from instaloader.instaloader import _ArbitraryItemFormatter, _PostPathFormatter
import os
import time


class Instagram_Scraper():
    def __init__(self, hashtags, image_number):
        self.hashtags = hashtags
        self.image_number = image_number
        # make the directory for instagram if they dont exist
        cwd = os.getcwd()
        if not os.path.isdir("{}/database/instagram".format(cwd)):
            os.makedirs("{}/database/instagram".format(cwd))

    def download_post_with_one_hashtag(self, loader, hashtag):
        count = 0
        #set the directory name the same as the hashtag
        loader.dirname_pattern = "database/instagram/{}".format(hashtag)
        caption_folder = "database/instagram/{}/captions".format(hashtag)

        print("--- Downloading post(s) with {} hashtag ---".format(hashtag))
        for post in loader.get_hashtag_posts(hashtag):
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
        loader.dirname_pattern = "database/instagram/{}".format(joined_hashtags)
        caption_folder = "database/instagram/{}/captions".format(joined_hashtags)
        #set the second hashtag as the filter
        filter = filterstr_to_filterfunc("'{}' in caption_hashtags".format(two_hashtags[1]), Post)

        print("--- Downloading post(s) with {} hashtags ---".format(', '.join(two_hashtags)))
        for post in loader.get_hashtag_posts(two_hashtags[0]):
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

    def instagram_scraper(self):
        download_option = input("(1) Image only (2) Video only (3) Both Image and video: ")
        # initialize the instaloader instance
        loader = None
        if download_option == '1':
            loader = Instaloader(
                sleep=True, quiet=False, filename_pattern='{date}', download_pictures=True,
                download_videos=False, download_video_thumbnails=True, download_geotags=False,
                download_comments=False, save_metadata=False, post_metadata_txt_pattern='')
        elif download_option == '2':
            loader = Instaloader(
                sleep=True, quiet=False, filename_pattern='{date}', download_pictures=False,
                download_videos=True, download_video_thumbnails=False, download_geotags=False,
                download_comments=False, save_metadata=False, post_metadata_txt_pattern='')
        elif download_option == '3':
            loader = Instaloader(
                sleep=True, quiet=False, filename_pattern='{date}', download_pictures=True,
                download_videos=True, download_video_thumbnails=False, download_geotags=False,
                download_comments=False, save_metadata=False, post_metadata_txt_pattern='')
        # login to a premade account to minimize chance of getting banned from instagram
        loader.login('webscrapingtool.rug', 'w3bscr4p1ng')

        hashtag_option = input("Enter (1) to download with one hashtag or (2) to download with two hashtag: ")
        if hashtag_option == '1':
            for hashtag in self.hashtags:
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
                self.download_post_with_two_hashtag(loader, self.hashtags)
            except Exception as e:
                pass
