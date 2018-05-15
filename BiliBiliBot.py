import praw
import config
import time

def bot_login():
	r = praw.Reddit(username = config.username,
					password = config.password,
					client_id = config.client_id,
					client_secret = config.client_secret,
					user_agent = "Bilibili MMD Reddit bot v0.1")
	print("Logged in")

	return r


## Main ------------------------------------------------------------
r = bot_login()