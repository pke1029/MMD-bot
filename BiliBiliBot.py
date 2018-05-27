import requests
from bs4 import BeautifulSoup
import praw
import config
import time

def bot_search():
	# url for Bilibili "douga" category daily ranking
	url = "https://www.bilibili.com/ranking/all/1/0/1"

	# making soup
	respond = requests.get(url)
	data = respond.text
	soup = BeautifulSoup(data, "lxml")
	ranking = soup.find_all('div', class_ = "info")

	# search for top submission with title containing "MMD" and get video id
	i = 0
	while i <= 100:
		div_attribute = ranking[i].a

		if "MMD" in div_attribute.text.upper():
			link = "https:" + div_attribute.get("href")
			char_list = list(link)
			video_id = "".join(char_list[-9:-1])
			print("Title:", div_attribute.text, ", video id:", video_id)
			return div_attribute.test, video_id

		else:
			i += 1

	# in case keyword not found
	print("No MMD found")

def bot_info(video_id):
	url = "https://www.bilibili.com/video/av" + video_id + "/"

	# making soup
	respond = requests.get(url)
	data = respond.text
	soup = BeautifulSoup(data, "lxml")

	user_div = soup.find('div', class_ = "user clearfix")
	time_div = soup.find('div', class_ = "tm-info tminfo")
	#view_div = soup.find('div', class_ = "number")

	vid_user = user_div.a.text
	vid_time = time_div.time.text
	#vid_view = view_div.span.get("title")

	print(vid_user, vid_time)
	return vid_user, vid_time




def bot_login():
	print("Logging in...")
	r = praw.Reddit(username = config.username,
					password = config.password,
					client_id = config.client_id,
					client_secret = config.client_secret,
					user_agent = "Bilibili MMD Reddit bot v0.1")
	print("Logged in")

	return r


# Main ------------------------------------------------------------

r = bot_login()

title, video_id = bot_search()
vid_user, vid_time = bot_info(video_id)


