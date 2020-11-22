import sys
import csv
import os
import time
from urllib.parse import urlparse
import requests
from PIL import Image
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager  # the library is webdriver-manager

#this function retrieves url of images found on google
def get_image_urls(keyword):
    # get the chrome browser to open headless
    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    # get the webpage of the url
    url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947" % (
        keyword)
    browser.get(url)
    time.sleep(1)

    image_urls = []
    image_count = 1
    print("Getting URLs of the images: ")
    for i in range(1, 800):
        try:
            imgurl = browser.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (str(i)))
            imgurl.click()
            time.sleep(0.3)
            images = browser.find_elements_by_class_name("n3VNCb")
            for image in images:
                # download images with jpg/png/jpeg extensions
                if (image.get_attribute("src")[-3:].lower() in ["jpg", "png", "jpeg", "gif", "svg"]):
                    sys.stdout.write("\rDownloaded URL(s): {}".format(image_count))
                    sys.stdout.flush()
                    time.sleep(0.1)
                    image_urls.append(image.get_attribute("src"))
                    image_count += 1
                    break
            # scroll to load more image
            browser.execute_script("window.scrollTo(0, " + str(i * 150) + ");")
            time.sleep(0.3)
        except Exception as e:
            print("Error while retrieving url: {}".format(e))
            pass

    print("{} URL(s) of {} downloaded".format((str(image_count)), keyword))
    browser.close()
    return image_urls

#TO DO fix the image count somehow it doesnt work, and also print line dynamically
def download_images(image_urls, keyword, descriptor_path, downloaded_images, image_number):
    keyword_path = "{}/database/google/{}".format(os.getcwd(), keyword)

    image_count = 0
    for i in range (downloaded_images, len(image_urls)):
        if image_count == image_number:
            break
        try:
            image_name = keyword + str(i) + '.jpg'
            image_path = os.path.join(keyword_path, image_name)
            image = requests.get(image_urls[i])
            # status code 200 means the image is succesfully downloaded
            if image.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(image.content)
                with open(descriptor_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([str(i)] + get_metadata(image_urls[i], image_path))
                image_count += 1
                sys.stdout.write("\rDownloaded Image(s): {}".format(image_count))
                sys.stdout.flush()
                time.sleep(0.1)
        # if it doesnt work, try another images
        except Exception as e:
            print("Error while downloading image: {}".format(e))
            pass

    return image_count

# this function returns a row of related data of an image
def get_metadata(image_url, image_path):
    parsed = urlparse(image_url)
    file_base = os.path.basename(parsed[2])  # show the path from the website
    file_name = os.path.splitext(file_base)[0]  # get the name of the image
    file_extension = os.path.splitext(file_base)[1]  # get the extensions of the image
    website = parsed[1]  # show network location
    image = Image.open(image_path)
    image_width = image.size[0]
    image_height = image.size[1]
    return [file_name, image_width, image_height, website, file_extension]

def google_scrape(keyword, image_number):
    # specify the path for both log and descriptors
    log_name = "google_log_" + keyword + ".txt"
    log_folder = "{}/database/google/log".format(os.getcwd())
    log_path = os.path.join(log_folder, log_name)

    keyword_path = "{}/database/google/{}".format(os.getcwd(), keyword)
    descriptor_name = 'google_' + keyword + '_descriptor.csv'
    descriptor_path = os.path.join(keyword_path, descriptor_name)

    image_urls = []
    downloaded_images = 0
    # if the user already downloaded some images before, we can see on the log
    if os.path.isfile(log_path):
        with open(log_path, "r") as file:
            for line in file:
                current_line = line[:-1]
                image_urls.append(current_line)
        downloaded_images = int(image_urls[-1])
        image_urls = image_urls[:-1]
    # if the user download images for the first time
    else:
        # write the obtained urls to a file
        image_urls = get_image_urls(keyword)
        with open(log_path, "w") as file:
            for url in image_urls:
                file.write('%s\n' % url)
        with open(descriptor_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Name", "Image Width", "Image height", "Website", "Extension"])

    #write the total number of downloaded image to the log file
    downloaded_images += download_images(image_urls, keyword, descriptor_path, downloaded_images, image_number)
    with open(log_path, "a") as file:
        file.write('%s\n' % str(downloaded_images))
