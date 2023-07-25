import requests
import time
import re
import csv
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
import os as system

def scrape(link):
    driver = webdriver.Firefox()
    driver.get(link)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source)
    article = soup.find('article')
    article_text = str(article)
    mainPagePostsElem = article_text.split("<a")
    driver.close()
    results = []
    for post in mainPagePostsElem:
        if(post.__contains__("href")):       
            postLink = post.split("href=\"")[1]
            postLink = postLink.split("\"")[0]
            postLink = f"https://www.instagram.com{postLink}"
            print(postLink)
            ##Get the post alt information 
            try:
                altInformation = post.split("img alt=\"")[1]
                altInformation = altInformation.split("\" class=\"")[0]
            except:
                altInformation = ''
            result = getPostInfo(postLink, altInformation)
            results.append(result)
    return results

def getPostInfo(postLink, altInformation = ''):
    page = requests.get(postLink)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup = str(soup)
    isVideoFlag = 0
    if(soup.__contains__("content=\"video\"")):
        isVideoFlag=1
        Content_type = "video"
    else:
        Content_type = "image"
    likes = getPostLikes(soup)
    comments = getPostComments(soup) 
    description = getDescription(soup)
    hashtags = getHashtags(description)
    time = getPostDate(postLink, isVideoFlag)
    return [postLink, time[0], time[1], Content_type, time[2], likes, comments, description, hashtags, altInformation]
     
def getPostLikes(information):
    likes = information.split("likes,")[0]
    separator = "'"
    likes = likes.split(separator)[-1]
    if(re.search('[a-zA-Z]', likes)):
        separator = "\""
        likes = likes.split(separator)[-1]
    return int(likes.strip())

def getPostComments(information):
    comments = information.split("comments")[0]
    return int(comments.split(",")[-1].strip())
    

def getDescription(information):
    description = information.split("<title>")[1]
    description = description.split("\"")[1]
    if description == "HasteSupportData":
        description = ""
    return description

def getHashtags(description):
    rawData = description.split("#")

    hashtags = []
    for index, hashtag in enumerate(rawData):
        if(index != 0):
            hashtag = hashtag.split(" ")[0]
            hashtag = hashtag.split("\n")[0]
            hashtags.append(f'#{hashtag}')

    return hashtags

def getPostDate(link, videoFlag = 0):
    driver = webdriver.Firefox()
    driver.get(link)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Get the video views
    views = 0
    if(videoFlag == 1):
        views = soup.find('span', class_='_aauw')
        views = str(views)
        views = views.split("<span>")[1]
        views = int(views.split("</span>")[0].strip())

    timev = soup.find('time')
    timev = str(timev)
    timev = timev.split("datetime=\"")[1]
    timev = timev.split("\"")[0]
    timev = timev.replace("T", " ")
    timev = timev.replace("Z", "")
    timev = timev.split(" ")
    driver.close()
    return [timev[0], timev[1], views]

def initializeCSV(fileName, results):
    with open(fileName, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["post", "day", "time", "content_type", "views", "likes", "comments", "description", "hashtags", "alt_information"])
        for result in results:
            escaped_result = [item.replace("\n", r"\n") if isinstance(item, str) else item for item in result]
            writer.writerow(escaped_result)

def createFolder(folderName):
    distFolder = f"./{folderName}"
    if not system.path.exists(distFolder):
        system.makedirs(distFolder)
    return distFolder

def main():
    fileName = "instagram"
    folder = createFolder("Results")      
    fileName = f"{folder}/{fileName}.csv"
    print(fileName)
    results = scrape("Enter the link of the instagram page")
    initializeCSV(fileName, results)



if __name__ == '__main__':
    main()
