import praw
import config
import time

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

#r = bot_login()


import requests
from bs4 import BeautifulSoup

def bot_search():
	# url for Bilibili "douga" category daily ranking
	url = "https://www.bilibili.com/ranking/all/1/0/1"

	# making soup
	r = requests.get(url)
	data = r.text
	soup = BeautifulSoup(data, "lxml")
	ranking = soup.find_all('div', class_ = "info")

	# search for top submission with title containing "MMD" and get video id
	for i in ranking:
		if "MMD" in i.a.text.upper():
			link = "https:" + i.a.get("href")
			char_list = list(link)
			video_id = "".join(char_list[-9:-1])
			print(video_id)

bot_search()

