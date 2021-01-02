import os
from google_scraper import Google_Scraper
from instagram_scraper import Instagram_Scraper
from twitter_scraper import Twitter_Scraper

def main():
    #read the txt file and put them to a list
    txtfile = open('classes.txt', 'r')
    keywords = txtfile.readlines()
    keywords = [keyword.strip() for keyword in keywords]

    if not os.path.isdir("{}/database/".format(os.getcwd())):
        os.makedirs("{}/database/".format(os.getcwd()))
    print("(1) Google")
    print("(2) Instagram")
    print("(3) Twitter")
    website = input("Enter 1, 2 or 3: ")
    print("")
    sample_number = int(input("Enter number of samples to be downloaded: "))
    print("")
    if website == '1':
        for keyword in keywords:
            google_scraper = Google_Scraper(keyword, sample_number)
            google_scraper.google_scrape()
    elif website == '2':
        instagram_scraper = Instagram_Scraper(keywords, sample_number)
        instagram_scraper.instagram_scraper()
    elif website == '3':
        for keyword in keywords:
            tp = Twitter_Scraper(keyword, sample_number)
            tp.twitter_scraper()

if __name__ == "__main__":
    main()