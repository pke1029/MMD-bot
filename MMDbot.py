# reddit bot for sharing mmd from Bilibili.com for r/mikumikudance subreddit
# by u/pke1029


import requests
from bs4 import BeautifulSoup
import praw
import time
import os


# search for MMD video from Bilibili daily ranking and list the video IDs
def bot_search():
    print("Obtaining video id...")
    # url for Bilibili "douga" category daily ranking
    url = "https://www.bilibili.com/ranking/all/1/0/1"

    # making soup
    respond = requests.get(url)
    data = respond.text
    soup = BeautifulSoup(data, "lxml")
    ranking = soup.find_all('div', class_="info")

    vid_id_list = []

    # search for top submission with title containing "MMD" and get video id
    for div in ranking:
        if "MMD" in div.a.text.upper():
            link = "https:" + div.a.get("href")
            char_list = list(link)
            video_id = "".join(char_list[-9:-1])
            vid_id_list.append(video_id)

    print("Video id obtained, %d found" % len(vid_id_list))

    return vid_id_list


# find the submitter name and submission time
def bot_info(video_id):
    print("Obtaining video info...")
    url = "https://www.bilibili.com/video/av" + video_id + "/"

    # making soup
    respond = requests.get(url)
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


# authenticate reddit login
def authenticate():
    print("Authenticating...")
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
            # no_repost_list = filter(None, no_repost_list)

    return no_repost_list


# search, post and comment
def run_bot(reddit, subreddit, no_repost_list):
    vid_id_list = bot_search()

    post = False

    # check video id to previous submission
    for vid_id in vid_id_list:
        if vid_id not in no_repost_list:

            url = "https://www.bilibili.com/video/av" + vid_id + "/"
            post_title = "id:" + vid_id + " [NSFW]"

            # submit link
            submission = subreddit.submit(title=post_title,
                                          url=url,
                                          send_replies=False)
            post = True
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
                         "was performed automagically."
                         "^[GitHub](https://github.com/pke1029/MMD-bot)")

            # post video info in comment
            submission.reply(post_info)
            print("Comment posted")

            break

    # in case no new MMD found
    if post is False:
        print("No new video found")


def main():
    # authenticate login
    reddit = authenticate()
    # go to subreddit
    subreddit = reddit.subreddit("test")
    # list previously posted video
    no_repost_list = get_saved_id()
    # search, post and comment
    run_bot(reddit, subreddit, no_repost_list)
    print("End of program. Developed by r/pke1029")


if __name__ == "__main__":
    main()
