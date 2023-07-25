import requests
import time
import re
import csv
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import os as system

def scrape(link):
    driver = webdriver.Firefox()
    driver.get(link)
    scrollDown(driver)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source)
    article = soup.find('article')
    article_text = str(article)
    mainPagePostsElem = article_text.split("<a")
    print(f'Nº posts found:{len(mainPagePostsElem)}')
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

def scrollDown(driver):    
    cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]")))
    cookies.click()
    time.sleep(2)
    logInButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[2]/section/nav/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[3]/div[1]/a")))
    logInButton.click()

    ##Log In credentials
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    username.send_keys("a")
    password.send_keys('a')

    submit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

    submit.click()    

    # not_now = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]/div[3]/div/div[3]/div/div')))

    # not_now.click()
    try:
        not_now = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="_ac8f"]')))
        not_now.click()
    except:
        not_now

    ##Scroll down
    old_position = 0
    new_position = None

    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        # Sleep and Scroll
        time.sleep(2)
        driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
        # Get new position
        new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
    
    one_third_postion = new_position*(1/3)
    two_third_position = new_position*(2/3)
    curr_position = one_third_postion
    max_posts = 0
    max_post_position = 0
    while(curr_position < two_third_position):
        driver.execute_script(f"window.scrollTo(0, {curr_position});")
        soup = BeautifulSoup(driver.page_source)
        article = soup.find('article')
        article_text = str(article)
        mainPagePostsElem = article_text.split("<a")
        if(len(mainPagePostsElem)>max_posts):
            max_posts = len(mainPagePostsElem)
            max_post_position = curr_position
        curr_position += 1000
    driver.execute_script(f"window.scrollTo(0, {max_post_position});")   
    print(new_position, curr_position, max_posts)
    print("stoped scrolling")



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
    try:
        likes = int(likes.strip())
    except:
        likes = 'Error'
    return likes

def getPostComments(information):
    comments = information.split("comments")[0]
    try:
        comments = int(comments.split(",")[-1].strip())
    except:
        comments = 'Error'
    return comments
    

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
    results = scrape("https://www.instagram.com/quantropi/")
    initializeCSV(fileName, results)


if __name__ == '__main__':
    main()
