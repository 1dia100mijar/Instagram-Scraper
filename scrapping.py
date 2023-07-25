import requests
import time
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver

def scappe(link):
    driver = webdriver.Firefox()
    driver.get(link)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source)
    article = soup.find('article')
    article_text = str(article)
    mainPagePostsElem = article_text.split("<a")
    driver.close()
    for post in mainPagePostsElem:
        if(post.__contains__("href")):
            post = post.split("href=\"")[1]
            post = post.split("\"")[0]
            postLink = f"https://www.instagram.com{post}"
            getPostInfo(postLink)
            print("\n\n\n--------------------------------------------------\n--------------------------------------------------\n\n\n")

def getPostInfo(postLink):
    print(postLink)
    page = requests.get(postLink)
    soup = BeautifulSoup(page.content, 'html.parser')
    soup = str(soup)
    likes = getPostLikes(soup)
    isVideoFlag = 0
    if(soup.__contains__("content=\"video\"")):
        isVideoFlag=1

    comments = getPostComments(soup) 
    description = getDescription(soup)
    hashtags = getHashtags(description)
    time = getPostDate(postLink, isVideoFlag)
    # print(likes)
    # print(description)
    # print(hashtags)
    # print(comments)
    # print(time)
    print(f'Post: {postLink}\nLikes: {likes}\nComments: {comments}\nDescription: {description}\nHashtags: {hashtags}\nTime: {time[0]}\n')
    if(isVideoFlag):
        print(f'Views: {time[1]}\n')

def getPostLikes(information):
    likes = information.split("likes,")[0]
    return likes.split("'")[-1]

def getPostViewes(information):
    views = information.split("views")[0]
    return views.split(",")[-1].strip()

def getPostComments(information):
    comments = information.split("comments")[0]
    return comments.split(",")[-1].strip()
    

def getDescription(information):
    description = information.split("<title>")[1]
    return description.split("\"")[1]

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
        views = views.split("</span>")[0]

    timev = soup.find('time')
    timev = str(timev)
    timev = timev.split("datetime=\"")[1]
    timev = timev.split("\"")[0]
    timev = timev.replace("T", " ")
    timev = timev.replace("Z", "")
    driver.close()
    return [timev, views]


def main():
    scappe("https://www.instagram.com/sportingcp/")


if __name__ == '__main__':
    main()
