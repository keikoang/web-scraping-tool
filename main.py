import os
from google_scraper import google_scrape

def main():
    #read the txt file and put them to a list
    txtfile = open('classes.txt', 'r')
    keywords = txtfile.readlines()
    keywords = [keyword.strip() for keyword in keywords]

    #make the directories for each keyword
    makeDirectories(keywords, 'google')
    image_number = int(input("Enter maximum number of images to be downloaded per keyword: "))
    for keyword in keywords:
        google_scrape(keyword, image_number)

#make folders based on the keywords and the website users use
def makeDirectories(keywords, website):
    #cwd = current working directory, make database directory if it doesnt exist
    cwd = os.getcwd()
    if not os.path.isdir("{}/database/".format(cwd)):
        os.makedirs("{}/database/".format(cwd))
    if not os.path.isdir("{}/database/{}/log".format(cwd, website)):
        os.makedirs("{}/database/{}/log".format(cwd, website))

    #make the directories for each keyword
    for keyword in keywords:
        #handle keyword that has space in it
        if " " in keyword:
            keyword = "_".join(keyword.split())
        if not os.path.isdir("{}/database/{}/{}".format(cwd, website, keyword)):
            os.makedirs("{}/database/{}/{}".format(cwd, website, keyword))

if __name__ == "__main__":
    main()