# Instagram-Scraper
Scrapper to get the information related to all post of a Instagram account


### Before running the program, make sure to have installed the following packages:
- requests
- bs4 
- selenium

You can install all at once with the following command:
> pip install requests bs4 selenium


### Insert your Instagram's account **username** and **password** on the lines:
```
username.send_keys("*username*")
password.send_keys("*password*")
```

## 🚨Browser compatibilities🚨
The program is designed use the Edge browser. You can change it to one that is supported by the Selenium library, when the driver is being created in the line of code:
```
driver = webdriver.Edge()
```
Keep in mind that using other browsers, the final result isn't garanteed to be the same.
