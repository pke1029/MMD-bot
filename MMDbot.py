# reddit bot for sharing mmd from Bilibili.com for r/mikumikudance subreddit
# by u/pke1029


import requests
from bs4 import BeautifulSoup
import praw
import time
import os


# authenticate reddit login
def authenticate():
    print("\nAuthenticating...")
    reddit = praw.Reddit("MMDbot", user_agent="Bilibili MMD Reddit bot v0.1")
    print("Authenticating as {}".format(reddit.user.me()))

    return reddit


# read file containing video id of all previous submission
def get_saved_id():
    if not os.path.isfile("no_repost_list.txt"):
        no_repost_list = []
    else:
        with open("no_repost_list.txt", "r") as f:
            no_repost_list = f.read()
            no_repost_list = no_repost_list.split("\n")

    if not os.path.isfile("not_mmd_id.txt"):
        not_mmd_id = []
    else:
        with open("not_mmd_id.txt", "r") as f:
            not_mmd_id = f.read()
            not_mmd_id = not_mmd_id.split("\n")

    return no_repost_list, not_mmd_id


# search for MMD video from Bilibili daily ranking and list the video IDs
def bot_get_vid_id():
    print("Obtaining video id...")
    
    # url for Bilibili "douga" category daily ranking
    url = "https://www.bilibili.com/ranking/all/1/0/1"

    while True:
        try:
            respond = requests.get(url)
            break
        except:
            time.sleep(5)

    # making soup
    data = respond.text
    soup = BeautifulSoup(data, "lxml")
    ranking = soup.find_all('div', class_="info")

    vid_id_list = []

    # obtain all video id
    for div in ranking:
        link = "https:" + div.a.get("href")
        char_list = list(link)
        video_id = "".join(char_list[-9:-1])
        vid_id_list.append(video_id)

    print("Video id obtained")

    return vid_id_list


# check if video is taged as mmd
def is_mmd(vid_id):
    print('checking %s ...' % vid_id, end='')
    url = "https://www.bilibili.com/video/av" + vid_id + "/"

    while True:
        try:
            respond = requests.get(url)
            break
        except:
            time.sleep(5)

    data = respond.text
    soup = BeautifulSoup(data, "lxml")

    # get video tag
    tag_list = []
    tag_li = soup.find_all('li', class_="tag")
    for li in tag_li:
        tag_list.append(li.text)

    # check if video is taged as mmd
    if 'MMD.3D' in tag_list:
        print('O')
        return True
    else:
        print('X')
        return False


def search_mmd(vid_id_list, no_repost_list, not_mmd_id):
    print('searching for mmd...')
    vid_id_list_filtered = []

    rank = 1
    for vid_id in vid_id_list:
        if vid_id not in not_mmd_id and vid_id not in no_repost_list:

            # check if is mmd
            if is_mmd(vid_id):
                print('rank = %d' % rank)
                return vid_id

            else:
                not_mmd_id.append(vid_id)
                with open("not_mmd_id.txt", "a") as f:
                    f.write(vid_id + "\n")
                rank += 1

        else:
            rank += 1

    # if no new mmd found
    print("no new mmd found")
    return False


# find the submitter name and submission time
def bot_info(video_id):
    print("Obtaining video info...")
    url = "https://www.bilibili.com/video/av" + video_id + "/"

    while True:
        try:
            respond = requests.get(url)
            break
        except:
            time.sleep(5)

    data = respond.text
    soup = BeautifulSoup(data, "lxml")

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
def run_bot(reddit, subreddit, no_repost_list, not_mmd_id):
    vid_id_list = bot_get_vid_id()

    search = True
    while search is True:
        # search mmd
        vid_id = search_mmd(vid_id_list, no_repost_list, not_mmd_id)
        
        # if mmd found
        if vid_id is not False:
            url = "https://www.bilibili.com/video/av" + vid_id + "/"
            post_title = "id:" + vid_id + " [NSFW]"

            # submit link
            submission = subreddit.submit(title=post_title,
                                          url=url,
                                          send_replies=False)
            print("Sumbission posted")

            # save video id to make sure to not repost
            no_repost_list.append(vid_id)
            with open("no_repost_list.txt", "a") as f:
                f.write(vid_id + "\n")

            # get video info
            vid_title, vid_user, vid_time = bot_info(vid_id)
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
    subreddit = reddit.subreddit("test")
    # list previously posted video and checked video
    no_repost_list, not_mmd_id = get_saved_id()
    while True:
        # search, post and comment
        run_bot(reddit, subreddit, no_repost_list, not_mmd_id)
        # sleep for 15 minutes
        print("Sleeping...")
        time.sleep(960)
        # time.sleep(86400)     # 24hr
        # print("End of program. Developed by r/pke1029")


if __name__ == "__main__":
    main()
