# reddit bot for sharing mmd from nicovideo.jp for r/mikumikudance subreddit
# by u/pke1029

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import praw
import datetime
import time
import os



def make_soup(url):

    while True:
        try:
            respond = requests.get(url)
            break
        except:
            print("access denined")
            time.sleep(5)

    data = respond.text
    soup = BeautifulSoup(data, "lxml")

    return soup


def make_soup_js(url):

    # driver = webdriver.Chrome()
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver')
    
    while True:
        try:
            driver.get(url)
            time.sleep(3)
            respond = driver.page_source
            driver.quit()
            break
        except:
            print("access denined")
            time.sleep(5)

    # data = respond.text
    soup = BeautifulSoup(respond, "lxml")

    return soup


# authenticate reddit login
def authenticate():
    print("\nAuthenticating...")
    reddit = praw.Reddit("MMDbot", user_agent="Bilibili MMD Reddit bot v0.1")
    print("Authenticate as {}".format(reddit.user.me()))

    return reddit


# read file containing video id of all previous submissions
def get_nico_post_list():
    if not os.path.isfile("nico_post_list.txt"):
        nico_post_list = []
    else:
        with open("nico_post_list.txt", "r") as f:
            nico_post_list = f.read()
            nico_post_list = nico_post_list.split("\n")

    return nico_post_list


def get_nico_id_list():
    print("Obtaining video id...")
    
    # url = 'http://www.nicovideo.jp/tag/mmd?f_range=1&sort=v&order=d'    # daily
    url = "http://www.nicovideo.jp/tag/mmd?f_range=2&sort=v&order=d"    # weekly
    # url = 'http://www.nicovideo.jp/tag/mmd?f_range=3&sort=v&order=d'    # monthly
    soup = make_soup(url)

    # generating list
    nico_id_list = []
    ranking = soup.find_all("li", class_="item")
    for li in ranking:
        nico_id = li.get("data-video-id")
        if nico_id != None:
            nico_id_list.append(str(nico_id))

    print("Video id obtained")
    return nico_id_list


def is_nsfw(nico_id):

    keyword_list = ["R-18", "R18MMD"]
    # keyword_list2 = ["紳士向け", "紳士の社交場"]

    url = "http://www.nicovideo.jp/watch/" + nico_id
    soup = make_soup(url)

    # get video tag
    tag = soup.find_all("meta")[4].get("content")

    for keyword in keyword_list:
        if keyword in tag:
            return True
    return False


def get_info(nico_id):
    print("Obtaining video info...")

    url = "http://www.nicovideo.jp/watch/" + nico_id
    soup = make_soup_js(url)

    # webpage scraping for meta data
    title = soup.find('h1', 'VideoTitle').text
    user = soup.find('div', class_="VideoOwnerInfo-pageLinks").a.text
    time = soup.find('time', class_="VideoUploadDateMeta-dateTimeLabel").text

    print("Video info obtained \n title: %s submitter: %s time: %s"
        % (title, user, time))

    return title, user, time


def run_search_nico(reddit, subreddit, nico_post_list):
    nico_id_list = get_nico_id_list()
    
    post = False
    for nico_id in nico_id_list:
        if nico_id not in nico_post_list and is_nsfw(nico_id) is False:

            url = "http://www.nicovideo.jp/watch/" + nico_id
            post_title = "id:" + nico_id

            # submit link
            submission = subreddit.submit(title=post_title,
                                          url=url,
                                          send_replies=False)
            print("Sumbission posted")
            post = True

            # save video id to make sure to not repost
            nico_post_list.append(nico_id)
            with open("nico_post_list.txt", "a") as f:
                f.write(nico_id + "\n")

            # get video info
            title, user, time = get_info(nico_id)
            post_info = ("**Title:** " + title + "\n\n "
                         "**Submitter:** " + user + "\n\n "
                         "**Submission time:** " + time + "\n\n "
                         "---" "\n\n "
                         "I am a bot, and this action "
                         "was performed automagically. "
                         "^[GitHub](https://github.com/pke1029/MMD-bot)")

            # post video info in comment
            submission.reply(post_info)
            print("Comment posted")

            break

    if post is False:
        print("no new mmd found")


def main():
    # authenticate login
    reddit = authenticate()
    # go to subreddit
    subreddit = reddit.subreddit("test")
    # list previously posted video and checked video
    nico_post_list = get_nico_post_list()
    while True:
        run_search_nico(reddit, subreddit, nico_post_list)

        # sleep until next posting time 
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        next_post_time = datetime.combine(tomorrow, datetime.time(0, 0, 0))
        current_time = datetime.datetime.now()
        duration = next_post_time - current_time
        duration_second = duration.seconds
        print('sleeping for ' + duration + '...')
        time.sleep(duration_second)


if __name__ == "__main__":
    try:
        main()
    finally:
        print('\nEnd of programme, developed by pke1029')
