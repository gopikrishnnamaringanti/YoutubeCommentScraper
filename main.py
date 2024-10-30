import csv
import io
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time

def scrape(url):
    # WebDriver Set Up
    service = Service(r"C:\chromedriver.exe") 
    driver = webdriver.Chrome(service=service)

    # URL Navigation
    driver.get(url)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 10)  # 10 seconds wait

    try:
        # video title
        title = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/h1/yt-formatted-string'))).text
        # comment section
        comment_section = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="comments"]')))
    except exceptions.NoSuchElementException:
        print("Error: Double check selector OR element may not yet be on the screen at the time of the find operation")
        driver.quit()
        return

    # Scroll to comment section
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(2)

    # Scroll for more comments
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    comments_to_fetch = 200

    while len(driver.find_elements(By.XPATH, '//*[@id="content-text"]')) < comments_to_fetch:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Final Scroll
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract usernames and comments
        username_elems = driver.find_elements(By.XPATH, '//*[@id="author-text"]')
        comment_elems = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        print("Error: Double check selector OR element may not yet be on the screen at the time of the find operation")
        driver.quit()
        return

    print("> VIDEO TITLE: " + title + "\n")


    # Save results to CSV file
    with io.open('results.csv', 'w', newline='', encoding="utf-16") as file:
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Comment"])
        for username, comment in zip(username_elems[:comments_to_fetch], comment_elems[:comments_to_fetch]):
            writer.writerow([username.text, comment.text])

    driver.quit()

if __name__ == "__main__":
    scrape("https://www.youtube.com/watch?v=HZ_Q20ir-gg")
