# reddit bot for sharing mmd from Bilibili.com for r/mikumikudance subreddit
# by u/pke1029


import requests
from bs4 import BeautifulSoup
import praw
import datetime
import time
import os


# authenticate reddit login
def authenticate():
    print("\nAuthenticating...")
    reddit = praw.Reddit("MMDbot", user_agent="Bilibili MMD Reddit bot v0.1")
    print("Authenticating as {}".format(reddit.user.me()))

    return reddit


# read file containing video id of all previous submissions
def get_bili_post_list():
    if not os.path.isfile("bili_post_list.txt"):
        bili_post_list = []
    else:
        with open("bili_post_list.txt", "r") as f:
            bili_post_list = f.read()
            bili_post_list = bili_post_list.split("\n")

    return bili_post_list


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


# search for MMD video from Bilibili daily ranking and list the video IDs
def get_bili_id_list():
    print("Obtaining video id...")
    
    # url for Bilibili "douga" category ranking
    # url = "https://www.bilibili.com/ranking/all/1/0/1"      # daily
    url = "https://www.bilibili.com/ranking/all/1/0/3"      # three day
    # url = "https://www.bilibili.com/ranking/all/1/0/7"      # weekly
    # url = "https://www.bilibili.com/ranking/all/1/0/30"     # monthly

    soup = make_soup(url)
    ranking = soup.find_all('div', class_="info")

    bili_id_list = []

    # obtain all video id
    for div in ranking:
        link = "https:" + div.a.get("href")
        char_list = list(link)
        bili_id = "".join(char_list[-11:-1])
        bili_id_list.append(bili_id)

    print("Video id obtained")

    return bili_id_list


# check if video is taged as mmd
def is_mmd(bili_id):
    print('checking %s ...' % bili_id, end='')
    url = "https://www.bilibili.com/video/" + bili_id + "/"

    soup = make_soup(url)

    # get video tag
    tag_list = []
    tag_li = soup.find_all('li', class_="tag")
    for li in tag_li:
        tag_list.append(li.text)

    # O if is mmd, X if not
    if 'MMD.3D' in tag_list:
        print('O')
        return True
    else:
        print('X')
        return False


def search_mmd(bili_id_list, bili_post_list):
    print('searching for mmd...')

    # keep track ranking
    rank = 1

    for bili_id in bili_id_list:
        # check if video has been posted or not
        if bili_id not in bili_post_list and is_mmd(bili_id):

            print('rank = %d' % rank)
            return bili_id

        else:
            rank += 1

    # if no new mmd found
    print("no new mmd found")
    return False


# find the submitter name and submission time
def bot_info(bili_id):
    print("Obtaining video info...")
    url = "https://www.bilibili.com/video/" + bili_id + "/"
    
    soup = make_soup(url)
    
    # webpage scraping for video infomation
    title_div = soup.find('div', id="viewbox_report")
    user_div = soup.find('div', class_="user clearfix")
    time_div = soup.find('div', class_="tm-info tminfo")
    # views_div = soup.find('div', class_ = "number")

    vid_title = title_div.h1.text
    vid_user = user_div.a.text
    vid_time = time_div.time.text
    # vid_views = view_div.span.get("title")

    print("Video info obtained \n title: %s submitter: %s time: %s"
        % (vid_title, vid_user, vid_time))

    return vid_title, vid_user, vid_time


# search, post and comment
def run_bot(reddit, subreddit, bili_post_list):
    bili_id_list = get_bili_id_list()

    search = True
    while search is True:
        # search mmd
        bili_id = search_mmd(bili_id_list, bili_post_list)
        
        # if mmd found
        if bili_id is not False:
            url = "https://www.bilibili.com/video/" + bili_id + "/"
            # post_title = "id:" + bili_id + " [NSFW]"
            post_title = "id:" + bili_id

            # submit link
            submission = subreddit.submit(title=post_title,
                                          url=url,
                                          send_replies=False)
            print("Sumbission posted")

            # save video id to make sure to not repost
            bili_post_list.append(bili_id)
            with open("bili_post_list.txt", "a") as f:
                f.write(bili_id + "\n")

            # get video info
            vid_title, vid_user, vid_time = bot_info(bili_id)
            post_info = ("**Title:** " + vid_title + "\n\n "
                         "**Submitter:** " + vid_user + "\n\n "
                         "**Submission time:** " + vid_time + "\n\n "
                         "---" "\n\n "
                         "I am a bot, and this action "
                         "was performed automagically. "
                         "^[GitHub](https://github.com/pke1029/MMD-bot)")

            # post video info in comment
            submission.reply(post_info)
            print("Comment posted")

            search = False

        else:
            search = False


def main():
    # authenticate login
    reddit = authenticate()
    # go to subreddit
    # subreddit = reddit.subreddit("test")
    subreddit = reddit.subreddit("mikumikudance")
    # list previously posted video and checked video
    bili_post_list = get_bili_post_list()
    while True:
        # search, post and comment
        run_bot(reddit, subreddit, bili_post_list)
        
        # sleep until next posting time 
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        next_post_time = datetime.datetime.combine(tomorrow, datetime.time(8, 0, 0))
        current_time = datetime.datetime.now()
        duration = next_post_time - current_time
        duration_second = duration.seconds
        print('sleeping for', duration, '...')
        time.sleep(duration_second)


if __name__ == "__main__":
    try:
        main()
    finally:
        print('\nEnd of programme, developed by pke1029')
