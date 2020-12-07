import os
from google_scraper import Google_Scraper
from instagram_scraper import Instagram_Scraper

def main():
    #read the txt file and put them to a list
    txtfile = open('classes.txt', 'r')
    keywords = txtfile.readlines()
    keywords = [keyword.strip() for keyword in keywords]

    if not os.path.isdir("{}/database/".format(os.getcwd())):
        os.makedirs("{}/database/".format(os.getcwd()))
    website = input("Enter (1) for Google or (2) for instagram: ")
    image_number = int(input("Enter number of post(s) to be downloaded per keyword: "))
    if website == '1': #google
        for keyword in keywords:
            google_scraper = Google_Scraper(keyword, image_number)
            google_scraper.google_scrape()
    elif website == '2':
        instagram_scraper = Instagram_Scraper(keywords, image_number)
        instagram_scraper.instagram_scraper()

if __name__ == "__main__":
    main()