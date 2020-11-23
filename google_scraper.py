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


# this function click the button on the website
def click_button(browser, xpath):
    try:
        w = WebDriverWait(browser, 0.5)
        elem = w.until(expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
        elem.click()
    except:
        pass  # does nothing


# this function parse the page
def parse_page(keyword):
    # get the chrome browser to open headless
    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # get the webpage of the url
    url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947" % (
        keyword)
    browser.get(url)
    time.sleep(1)
    browser.maximize_window()

    print("--- Scrolling down the page for {} ---".format(keyword))
    # scroll down the page and click the show more button
    page_counter = 0
    scroll_height = .1
    while scroll_height < 9.9:
        sys.stdout.write("\rScrolled page: {}".format(page_counter))
        sys.stdout.flush()
        if page_counter < 10:
            click_button(browser, '//input[@type="button"]')
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
def save_images(image_boxes, keyword, log_path):
    print("--- Saving {} images information---".format(keyword))
    image_count = 0
    for image in image_boxes:
        src = image.get("data-src" or "src")
        if src is not None:
            try:
                img_caption = image.get("alt")
                img_width = str(image.get("width"))
                img_height = str(image.get("height"))
                with open(log_path, "a") as file:
                    file.write("{},{},{},{},{}\n".format(str(image_count), img_caption, src, img_width, img_height))
            except:
                continue  # continue to next image in image boxes
            image_count += 1
    print("Saved {} {} image(s)\n".format(image_count, keyword))


# this function download images from the link in the information file
def download_images(image_number, log_path, parsed_keyword, descriptor_path, downloaded_images):
    print("--- Downloading {} images ---".format(parsed_keyword))
    keyword_path = "{}/database/google/{}".format(os.getcwd(), parsed_keyword)
    image_counter = 0
    with open(log_path, "r") as file:
        for line in file:
            split_line = line.strip().split(',')
            index = int(split_line[0])
            if index < downloaded_images + 1:  # skip the downloaded images
                continue
            if index == image_number + downloaded_images + 1:  # break if already downloaded the required num of images
                break
            img_name = parsed_keyword + "_" + str(index) + ".jpg"
            img_link = split_line[2]
            try:
                urllib.request.urlretrieve(img_link, os.path.join(keyword_path, img_name))
                sys.stdout.write("\rDownloaded image: {}".format(image_counter))
                sys.stdout.flush()
                time.sleep(0.2)
            except:
                continue  # continue to next image if failed to download it
            with open(descriptor_path, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([split_line[0], split_line[1], split_line[3], split_line[4]])
            image_counter += 1
    sys.stdout.write("\rDownloaded image: {}".format(image_counter))
    sys.stdout.flush()
    print("\n")

def google_scrape(keyword, image_number):
    if " " in keyword:
        parsed_keyword = "_".join(keyword.split())
    else:
        parsed_keyword = keyword
    # specify the path for both log and descriptors
    log_folder = "{}/database/google/log".format(os.getcwd())
    log_name = "google_log_" + parsed_keyword + ".txt"
    d_log_name = "google_d_log_" + parsed_keyword + ".txt"
    log_path = os.path.join(log_folder, log_name)
    d_log_path = os.path.join(log_folder, d_log_name)

    keyword_path = "{}/database/google/{}".format(os.getcwd(), parsed_keyword)
    descriptor_name = 'google_' + keyword + '_descriptor.csv'
    descriptor_path = os.path.join(keyword_path, descriptor_name)

    downloaded_images = 0
    # if the user download images for the first time
    if not os.path.isfile(log_path):
        image_boxes = parse_page(keyword)
        save_images(image_boxes, keyword, log_path)
        with open(descriptor_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Image Caption", "Image Width", "Image height"])
        with open(d_log_path, 'w') as f:
            f.write("{}".format(str(0)))
    else:
        with open(d_log_path, 'r') as f:
            downloaded_images = int(f.read())

    download_images(image_number, log_path, parsed_keyword, descriptor_path, downloaded_images)
    with open(d_log_path, 'w') as f:
        f.write("{}".format(str(image_number + downloaded_images)))
