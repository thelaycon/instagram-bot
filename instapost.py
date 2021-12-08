import pathlib
import re
import time
import pickle
import csv
import requests
import pandas as pd
import pyautogui
from apscheduler.schedulers.background import BlockingScheduler
from selenium.webdriver import Firefox



scheduler = BlockingScheduler(timezone="Europe/Berlin")

start_date = input("Start date eg. 11/12/1945 : ")
end_date = input("End date eg. 11/12/1945 : ")
#user = input("Username: ").strip()
#passwd = input("Password: ").strip()

#Download image
#Post to Instagram

BASE_DIR = pathlib.Path(__file__).parent.resolve()
df = pd.read_csv("data.csv").values.tolist()

def reform(dt):
    new_date = dt.strftime("%#m/%#d/%Y")
    return new_date

def to_post():
    sched = []
    dates = list(map(reform, pd.date_range(start=start_date, end=end_date)))
    for row in df:
        match = re.search(r'(\d+/\d+/\d+)', row[3])
        if match != None:
            date_ = match.group(1)
            if date_ in dates:
                sched.append(row)
    return iter(sched)

to_post = to_post()

def fetch_image(uri, name):
    resp = requests.get(uri)
    with open(name, "wb") as f:
        f.write(resp.content)
    return True


def disable_notification(driver):
    try:
        driver.find_element_by_xpath("//*[contains(text(), 'Not Now')]").click()
    except:
        pass


def post(driver):
    desc = ""
    name = ""
    try:
        current = next(to_post)
        print("Fetching image for {}".format(current[4]))
        name = str(BASE_DIR) + "\\" + current[17].split("/")[-1]
        if fetch_image(current[17], name):
            print("Sucessfully fetched image")
        else:
            print("An error occured while fetching image")
        desc = current[9]
    except StopIteration:
        print("No product to post")
        return

    driver.find_element_by_xpath("/html/body/div[8]/div[2]/div/div/div/div[2]/div[1]/div/div/div[2]/div/button").click()
    time.sleep(15)
    pyautogui.typewrite(name)
    time.sleep(5)
    pyautogui.press("enter")
    time.sleep(15)
    driver.find_element_by_xpath("/html/body/div[6]/div[2]/div/div/div/div[1]/div/div/div[2]/div/button").click()
    time.sleep(5)
    driver.find_element_by_xpath("/html/body/div[6]/div[2]/div/div/div/div[1]/div/div/div[2]/div/button").click()
    driver.find_element_by_xpath("/html/body/div[6]/div[2]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/textarea").send_keys(desc)
    time.sleep(5)
    driver.find_element_by_xpath("/html/body/div[6]/div[2]/div/div/div/div[1]/div/div/div[2]/div/button").click()
    time.sleep(20)
    driver.find_element_by_xpath("/html/body/div[6]/div[1]/button").click()

    print("Successfully posted the image")
    print("Closing window")
    driver.close()


def automate(driver):
    #Check if cookies exist:
    try:
        print("Visiting instagram")
        driver.get("https://instagram.com")
        print("Loading cookies")
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        print("Cookies loaded, now refreshing")
        time.sleep(5)
        disable_notification(driver)
        driver.find_element_by_xpath("/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[3]/div/button").click()
        print("About to post")
        post(driver)
    except:
        print("Visiting Instagram")
        driver.get("https://instagram.com")
        time.sleep(5)
        username = driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[1]/div/label/input")
        password = driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[2]/div/label/input")
        print("Logging in")
        username.send_keys("09053001561")
        password.send_keys("richyrush4382")
        driver.find_element_by_xpath("/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]/button").click()
        print("Sleep for 20 seconds to solve captcha if any")
        time.sleep(20)

        #Export cookies
        print("Exporting cookies")
        pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))
        driver.get("https://instagram.com")
        disable_notification(driver)
        driver.find_element_by_xpath("/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[3]/div/button").click()
        print("About to post")
        post(driver)


def automate_it():
    print("Launching selenium") 
    driver = Firefox()
    print("Launched")
    try:
        automate(driver)
    except:
        print("An unexpected error occurred, now skipping this.")


print("First run")
automate_it()
print("Scheduling next job for 60 minutes")
scheduler.add_job(automate_it, "interval", minutes=2)
scheduler.start()
