import time
import os
import requests
import csv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager #the library is webdriver-manager
from urllib.parse import urlparse
from PIL import Image

def get_images_urls(keyword, image_number):
    #get the chrome browser to open headless
    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    #this url provides images that are not copyright
    url = "https://www.google.com/search?q="+keyword+"&tbm=isch&tbs=sur%3Afc&hl=en&ved=0CAIQpwVqFwoTCKCa1c6s4-oCFQAAAAAdAAAAABAC&biw=1251&bih=568"
    browser.get(url)
    time.sleep(2)

    #make a set, to prevent duplicate images
    image_urls = set()
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
            time.sleep(1)
            images = browser.find_elements_by_class_name("n3VNCb")
            for image in images:
                #download images with jpg/png/jpeg extensions
                if (image.get_attribute("src")[-3:].lower() in ["jpg", "png", "jpeg"]):
                    print("%d. %s" % (image_count, image.get_attribute("src")))
                    image_urls.add(image.get_attribute("src"))
                    image_count += 1
                    break
            #scroll to load more image
            browser.execute_script("window.scrollTo(0, " + str(i * 150) + ");")
            time.sleep(1)
        except Exception as e:
            print("Unable to get the link for this image")

    browser.close()
    return image_urls

def download_images(images_urls, keyword):
    #specify the download path based on keyword
    keyword_path = "{}/database/google/{}".format(os.getcwd(), keyword)
    #create the csv file and append the first row (column description)
    descriptor_name = 'google_'+keyword+'_descriptor.csv'
    descriptor_path = os.path.join(keyword_path, descriptor_name)
    with open(descriptor_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Image Width", "Image height", "Website", "Extension"])
    for i, image_url in enumerate(images_urls):
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
                    writer.writerow(get_metadata(image_url, image_path))
        #if it doesnt work, try another images
        except:
            print("Unable to download image "+ str(i))
            pass

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

download_images(get_images_urls('cat', 10), 'cat')
