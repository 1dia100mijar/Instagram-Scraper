import requests
import time
import re
import csv
from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import os as system

def scrape(driver, link):
    driver.get(link)
    logIn(driver)

    posts = {}
    ##Scroll down
    old_position = 0
    new_position = None
    while new_position != old_position:
        # Get old scroll position
        old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                 " window.pageYOffset : (document.documentElement ||"
                 " document.body.parentNode || document.body);"))
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        article = soup.find('article')
        article_text = str(article)
        htmlAelems = article_text.split("<a")
        aux = 1
        for elem in htmlAelems:
            if(elem.__contains__("href")):
                #Get post link
                postLink = elem.split("href=\"")[1]
                postLink = postLink.split("\"")[0]
                postLink = f"https://www.instagram.com{postLink}"
                #Get post alt information
                try:
                    alt = elem.split('img alt=\"')[1]
                    alt = alt.split("\"")[0]
                except:
                    alt = ''
                posts[postLink] = alt
        # Move down
        new_position = scroll(driver, old_position)
    
    print(f"Found {len(posts)} posts")
    results = []
    for link, altInformation in posts.items():
        print(f'Getting post information... "{link}"')
        result = getPostInfo(driver, link, altInformation)
        results.append(result)
    return results

def scroll(driver, old_position):
    next_position = old_position + 700
    driver.execute_script(f"window.scrollTo(0, {next_position});")
    # Get new position
    return driver.execute_script(("return (window.pageYOffset !== undefined) ?"
                " window.pageYOffset : (document.documentElement ||"
                " document.body.parentNode || document.body);"))

def logIn(driver):    
    cookies = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/button[1]")))
    cookies.click()
    time.sleep(2)
    logInButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[2]/section/nav/div[2]/div/div/div[3]/div/div/div[1]/div/div/div/div[3]/div[1]/a")))
    logInButton.click()

    ##Log In credentials
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='username']")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']")))

    print("Logging in...")
    username.send_keys("*username*")
    password.send_keys("*password*")

    submit = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))

    submit.click()

    not_now = None
    try:
        not_now = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[class="_ac8f"]')))
        not_now.click()
    except:
        not_now = None

def getPostInfo(driver, postLink, altInformation = ''):
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
    time = getPostDate(driver, postLink, isVideoFlag)
    return [postLink, time[0], time[1], Content_type, time[2], likes, comments, description, hashtags, altInformation]
     
def getPostLikes(information):
    likes = information.split(" likes,")[0]
    likes = likes.split("'")[-1]

    if(re.search('[a-zA-Z]', likes)):
        likes = likes.split("\"")[-1].strip()
    try:
        if(likes[-1] != "K" and likes[-1] != "M"):
            likes = int(likes.strip())
    except:
        likes = 'Error'
    return likes

def getPostComments(information):
    comments = information.split("comments")[0]
    try:
        comments = comments.split(",")[-1].strip()
        if(comments[-1] != "K" and comments[-1] != "M"):
            comments = int(comments)
    except:
        comments = 'Error'
    return comments
    

def getDescription(information):
    description = information.split("<title>")[1]
    description = description.split("\"")[1]
    description = description.split("\"</title>")[0]
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

def getPostDate(driver, link, videoFlag = 0):
    driver.get(link)
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Get the video views
    views = 0
    if(videoFlag == 1):
        views = soup.find('span', class_='_aauw')
        views = str(views)
        views = views.split("<span>")[1]
        views = int(views.split("</span>")[0].strip())

    timev = soup.find(class_='_aaqe')
    timev = str(timev)
    timev = timev.split("datetime=\"")[1]
    timev = timev.split("\"")[0]
    timev = timev.replace("T", " ")
    timev = timev.replace("Z", "")
    timev = timev.split(" ")
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
    print("Welcome to the Instagram Scraper")
    print("Please enter the following information")
    fileName = input("File name: ")
    fileName = f'{fileName}.csv'
    link = input("Instagram link: ")
    folder = createFolder("Results")    
    fileDir = f"{folder}/{fileName}"

    print("Creating driver...")
    driver = webdriver.Edge()
    
    results = scrape(driver, link)
    driver.close()
    initializeCSV(fileDir, results)
    
    print("\n\nDone!")
    print(f'The csv file {fileName} was saved in the Results directory')

if __name__ == '__main__':
    main()
