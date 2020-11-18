import time
import os
import requests
import csv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager #the library is webdriver-manager
from urllib.parse import urlparse
from PIL import Image

def get_image_urls(keyword, image_number, image_urls):
    #get the chrome browser to open headless
    #options = webdriver.ChromeOptions()
    #options.headless = True
    browser = webdriver.Chrome(ChromeDriverManager().install())

    #this url provides images that are not copyright
    url = "https://www.google.com/search?q=%s&source=lnms&tbm=isch&sa=X&ved=2ahUKEwie44_AnqLpAhUhBWMBHUFGD90Q_AUoAXoECBUQAw&biw=1920&bih=947"%(keyword)
    browser.get(url)
    time.sleep(2)

    image_count = 1
    #image_number*2 here, so the program could anticipate for images that are not in preferred extension
    # and also anticipate for images that the program couldn't get the link for
    for i in range (1, image_number * 2):
        #if the number fof images found satisfies the requirement, simply quit
        if len(image_urls) == image_number:
            break
        try:
            imgurl = browser.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img' % (str(i)))
            imgurl.click()
            time.sleep(0.7)
            images = browser.find_elements_by_class_name("n3VNCb")
            for image in images:
                #download images with jpg/png/jpeg extensions
                if (image.get_attribute("src")[-3:].lower() in ["jpg", "png", "jpeg", "gif", "svg"]):
                    print("%d. %s" % (image_count, image.get_attribute("src")))
                    image_urls.append(image.get_attribute("src"))
                    image_count += 1
                    break
            #scroll to load more image
            browser.execute_script("window.scrollTo(0, " + str(i * 150) + ");")
            time.sleep(0.6)
        except Exception as e:
            print("Unable to get the link for this image")

    browser.close()
    return image_urls

def download_images(images_url, keyword, descriptor_path):
    keyword_path = "{}/database/google/{}".format(os.getcwd(), keyword)

    for i, image_url in enumerate(images_url):
        try:
            image_name = keyword+str(i)+'.jpg'
            image_path = os.path.join(keyword_path, image_name)
            image = requests.get(image_url)
            #status code 200 means the image is succesfully downloaded
            if image.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(image.content)
                with open(descriptor_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([str(i)]+get_metadata(image_url, image_path))
        #if it doesnt work, try another images
        except:
            print("Unable to download image "+ str(i))
            pass

#this function returns a row of related data of an image
def get_metadata(image_url, image_path):
    parsed = urlparse(image_url)
    file_base = os.path.basename(parsed[2]) #show the path from the website
    file_name = os.path.splitext(file_base)[0] #get the name of the image
    file_extension = os.path.splitext(file_base)[1] #get the extensions of the image
    website = parsed[1] #show network location
    image = Image.open(image_path)
    image_width = image.size[0]
    image_height = image.size[1]
    return [file_name, image_width, image_height, website, file_extension]

def google_scrape(keyword, image_number):
    #specify the path for both log and descriptors
    log_name = "google_log_"+keyword+".txt"
    log_folder = "{}/database/google/log".format(os.getcwd())
    log_path = os.path.join(log_folder, log_name)

    keyword_path = "{}/database/google/{}".format(os.getcwd(), keyword)
    descriptor_name = 'google_' + keyword + '_descriptor.csv'
    descriptor_path = os.path.join(keyword_path, descriptor_name)

    #if the user already downloaded some images before, we can see on the log
    if os.path.isfile(log_path):
        with open(log_path, "r") as file:
            file_lines = file.read()
            image_urls = file_lines.split("\n")
    #if the user download images for the first time
    else:
        image_urls = []
        with open(descriptor_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Name", "Image Width", "Image height", "Website", "Extension"])

    #write the obtained urls to a file
    image_urls = get_image_urls(keyword, image_number, image_urls),
    with open(log_path, "w") as file:
        urls_in_lines = "\n".join(image_urls)
        file.write(urls_in_lines)
    download_images(image_urls, keyword, descriptor_path)