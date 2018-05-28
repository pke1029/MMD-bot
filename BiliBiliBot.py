import requests
from bs4 import BeautifulSoup
import praw
import config
import time
import os

# search for MMD video from Bilibili daily ranking
def bot_search():
	print("Obtaining video id...")
	# url for Bilibili "douga" category daily ranking
	url = "https://www.bilibili.com/ranking/all/1/0/1"

	# making soup
	respond = requests.get(url)
	data = respond.text
	soup = BeautifulSoup(data, "lxml")
	ranking = soup.find_all('div', class_ = "info")

	vid_id_list = []

	# search for top submission with title containing "MMD" and get video id
	for i in ranking:
		if "MMD" in i.a.text.upper():
			link = "https:" + i.a.get("href")
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

	title_div = soup.find('div', id = "viewbox_report")
	user_div = soup.find('div', class_ = "user clearfix")
	time_div = soup.find('div', class_ = "tm-info tminfo")
	#view_div = soup.find('div', class_ = "number")

	vid_title = title_div.h1.text
	vid_user = user_div.a.text
	vid_time = time_div.time.text
	#vid_view = view_div.span.get("title")

	print("Vidoe info obtained \n title: %s submitter: %s time: %s" % (vid_title, vid_user, vid_time))
	return vid_title, vid_user, vid_time

# login to reddit
def bot_login():
	print("Logging in...")
	r = praw.Reddit(username = config.username,
					password = config.password,
					client_id = config.client_id,
					client_secret = config.client_secret,
					user_agent = "Bilibili MMD Reddit bot v0.1")
	print("Logged in")

	return r

# read archived post
def get_saved_id():
	if not os.path.isfile("no_repost_list.txt"):
		no_repost_list = []
	else:
		with open("no_repost_list.txt","r") as f:
			no_repost_list = f.read()
			no_repost_list = no_repost_list.split("\n")
			# no_repost_list = filter(None, no_repost_list)

	return no_repost_list

def run_bot(r, subreddit, no_repost_list):
	vid_id_list = bot_search()

	for i in vid_id_list:
		if i not in no_repost_list:
			url = "https://www.bilibili.com/video/av" + i + "/"
			post_title = "id:" + i + " [NSFW]"

			s = subreddit.submit(title = post_title, url = url,  send_replies = False)
			print("Sumbission posted")
			
			no_repost_list.append(i)
			with open ("no_repost_list.txt", "a") as f:
				f.write(i + "\n")

			vid_title, vid_user, vid_time = bot_info(i)			
			post_info = "**Title:**" + vid_title + "\n\n **Submitter:**" + vid_user + "\n\n **Submission time:**" + vid_time + "\n\n --- \n\n I am a bot, and this action was performed automagically.^[GitHub](https://github.com/pke1029/MMD-bot)"

			submission =  r.submission(id = s.id)
			submission.reply(post_info)
			print("Comment posted")

			break


# Main ------------------------------------------------------------

r = bot_login()
subreddit = r.subreddit('test')
no_repost_list = get_saved_id()
run_bot(r, subreddit, no_repost_list)



