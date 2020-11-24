import sys
import csv
import os
import time
import urllib

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager  # the library is webdriver-manager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

class Google_Scraper():
    def __init__(self, keyword, image_number):
        self.keyword = keyword
        parsed_keyword = keyword
        if " " in keyword:
            parsed_keyword = "_".join(keyword.split())
        self.parsed_keyword = parsed_keyword
        self.image_number = image_number

        # specify the path for both log and descriptors
        log_folder = "{}/database/google/log".format(os.getcwd())
        keyword_folder = "{}/database/google/{}".format(os.getcwd(), parsed_keyword)
        log_name = "google_log_" + parsed_keyword + ".txt"
        d_log_name = "google_d_log_" + parsed_keyword + ".txt"
        descriptor_name = 'google_' + keyword + '_descriptor.csv'
        self.log_path = os.path.join(log_folder, log_name)
        self.d_log_path = os.path.join(log_folder, d_log_name)
        self.descriptor_path = os.path.join(keyword_folder, descriptor_name)

    # this function click the button on the website
    def click_button(self, browser, xpath):
        try:
            w = WebDriverWait(browser, 0.5)
            elem = w.until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
            elem.click()
        except:
            pass  # does nothing

    # this function parse the page
    def parse_page(self):
        options = webdriver.ChromeOptions() # get the chrome browser to open headless
        options.headless = True
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        # get the webpage of the url
        url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947" % (
            self.keyword)
        browser.get(url)
        time.sleep(1)
        browser.maximize_window()

        print("--- Scrolling down the page for {} ---".format(self.keyword))
        # scroll down the page and click the show more button
        page_counter = 0
        scroll_height = .1
        while scroll_height < 9.9:
            sys.stdout.write("\rScrolled page: {}".format(page_counter))
            sys.stdout.flush()
            if page_counter < 10:
                self.click_button(browser, '//input[@type="button"]')
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scroll_height)
            scroll_height += .03
            time.sleep(0.3)
            page_counter += 1
        print("\n")

        page = browser.page_source
        html = bs(page, "html.parser")
        image_boxes = html.find_all("img", {"class": "rg_i Q4LuWd"})
        browser.close()
        return image_boxes

    # this function save the images information on a file
    def save_images(self, image_boxes):
        print("--- Saving {} images information---".format(self.keyword))
        image_count = 1
        for image in image_boxes:
            src = image.get("data-src" or "src")
            if src is not None:
                try:
                    img_caption = image.get("alt")
                    img_width = str(image.get("width"))
                    img_height = str(image.get("height"))
                    with open(self.log_path, "a") as file:
                        file.write(
                            "{},{},{},{},{}\n".format(str(image_count), img_caption, src, img_width, img_height))
                except:
                    continue  # continue to next image in image boxes
                image_count += 1
        print("Saved {} {} image(s)\n".format(image_count-1, self.keyword))

    # this function download images from the link in the information file
    def download_images(self, downloaded_images, downloaded_index):
        print("--- Downloading {} images ---".format(self.parsed_keyword))
        keyword_path = "{}/database/google/{}".format(os.getcwd(), self.parsed_keyword)
        image_counter = 0
        with open(self.log_path, "r") as file:
            for line in file:
                split_line = line.strip().split(',')
                index = int(split_line[0])
                if index < downloaded_index + 1:  # skip the downloaded images
                    continue
                if image_counter == self.image_number:  # break if already downloaded the required num of images
                    index -= 1
                    break
                img_name = self.parsed_keyword + "_" + str(downloaded_images+image_counter+1) + ".jpg"
                img_link = split_line[2]
                try:
                    urllib.request.urlretrieve(img_link, os.path.join(keyword_path, img_name))
                    sys.stdout.write("\rDownloaded image: {}".format(image_counter))
                    sys.stdout.flush()
                    time.sleep(0.2)
                except:
                    continue  # continue to next image if failed to download it
                with open(self.descriptor_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([split_line[1], split_line[3], split_line[4]])
                image_counter += 1
        sys.stdout.write("\rDownloaded image: {}".format(image_counter))
        sys.stdout.flush()
        print("\n")
        if image_counter < self.image_number:
            print("You have downloaded all {} images. No more {} images are available to be downloaded".format(self.keyword, self.keyword))
        return image_counter+downloaded_images, index #total downloaded images and index of the last downloaded image

    def google_scrape(self):
        downloaded_images = 0
        downloaded_index = 0
        # if the user download images for the first time
        if not os.path.isfile(self.log_path):
            image_boxes = self.parse_page()
            self.save_images(image_boxes)
            with open(self.descriptor_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Image Caption", "Image Width", "Image height"])
            with open(self.d_log_path, 'w') as f:
                f.write("{}".format(str(0)))
        else:
            with open(self.d_log_path, 'r') as f:
                line = f.readline().strip().split(',')
                downloaded_images = int(line[0])
                downloaded_index = int(line[1])

        downloaded_images, downloaded_index = self.download_images(downloaded_images, downloaded_index)
        with open(self.d_log_path, 'w') as f: #write the total downloaded image and index of last downloaded image
            f.write("{}".format(str(downloaded_images) + ',' + str(downloaded_index)))
