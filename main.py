import os

def main():
    #read the txt file and put them to a list
    txtfile = open('classes.txt', 'r')
    keywords = txtfile.readlines()
    keywords = [keyword.strip() for keyword in keywords]

    #make the directories for each keyword
    makeDirectories(keywords, 'google')

#make folders based on the keywords and the website users use
def makeDirectories(keywords, website):
    #cwd = current working directory
    cwd = os.getcwd()
    #make the directories if they dont exist
    for keyword in keywords:
        if not os.path.isdir("{}/database/".format(cwd)):
            os.makedirs("{}/database/".format(cwd))
        if not os.path.isdir("{}/database/{}/{}".format(cwd, website, keyword)):
            os.makedirs("{}/database/{}/{}".format(cwd, website, keyword))

if __name__ == "__main__":
    main()