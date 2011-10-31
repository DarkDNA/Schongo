# -*- coding: utf-8 -*-
"""Sniffs URLs and shows the title for them, with special detection for sniffing youtube URLs"""

import urllib.request
import urllib.error
import xml.dom.minidom as dom
import re
from modules._utils import prettyNumber, prettyTime, unescapeHtml
import threading

archive = dict()


READ_SIZE = 32000;

__info__ = {
	"Author": "Selig Arkin",
	"Version": "1.0b",
	"Dependencies": []
}


ytRegEx = re.compile(r"(https?://)?(www\.)?youtu(be\.com/watch\?[^ ]*v=|\.be/)([^& ]+)")
twitterRegEx = re.compile(r"(https?://)?twitter.com/(#!/)?[a-zA-Z0-9_]+/status/(\d+)")

genRegEx = re.compile(r"https?://([^ ]+)")
titleRegEx = re.compile(r"<title>(.+)</title>")
titleMimes = [ "text/html" ]

def addStatusToArchive(ctx, s, prefix):
	global archive
	chan = ctx.chan
	if chan in archive:
		archive[chan].insert(0, (prefix, s))
	elif chan not in archive:
		archive[chan] = list()
		archive[chan].append((prefix, s))

	if len(archive[chan]) > 5:
		archive[chan] = archive[chan][:5]

def outputStatusArchive(ctx):
	global archive
	if archive.has_key(ctx.chan):
		if len(archive[ctx.chan]) > 0:
			for msg, prefix in archive[ctx.chan]:
				ctx.reply(msg, prefix);
			
		else:
			ctx.reply("Empty log", "UrlLog")
	else:
		ctx.reply("Empty log", "UrlLog")

def showTitle(ctx, url):
	ytMatch = ytRegEx.match(url)
	if ytMatch:
		showYouTube(ctx, ytMatch.group(4))
		return

	twitMatch = twitterRegEx.match(url)
	if twitMatch:
		showTwitter(ctx, twitMatch.group(3))
		return

	s = "Url: %s" % url

	encoding = None
	
	try:
		u = urllib.request.urlopen(url)
		stuff = u.read(READ_SIZE)
		newurl = u.url
		mime = u.info().get_content_type()
		encoding = u.info().get_param("charset")
		u.close()
	except urllib.error.HTTPError as e:
		# Intentionally not adding this to the archive, no point spamming unparsable URLs
		s += " • Failed to get information, HTTP Error: %d." % e.code
		ctx.reply(s, "UrlLog")
		return
	except urllib.error.URLError as e:
		s += " • Failed to get information: URL Error: %s." % e.reason
		ctx.reply(s, "UrlLog")
		return

	if encoding is None:
		encoding = "utf-8"
	
	# Look again after reading it in, to see if it is a shortened youtube url.

	m = ytRegEx.match(newurl)
	if m is not None:
		showYouTube(ctx, m.group(4))
		return

	twitMatch = twitterRegEx.match(newurl)
	if twitMatch:
		showTwitter(ctx, twitMatch.group(3))
		return


	if newurl != url:
		s += " • Redirects to: %s" % newurl

	if mime not in titleMimes:
		s += " • MIME type: %s" % mime

	if mime in titleMimes:
		stuff = stuff.decode(encoding)

		titleSearch = titleRegEx.search(stuff)
		if titleSearch is not None:
			s += " • Title: %s" % unescapeHtml(titleSearch.group(1))
		else:
			s += " • Could not find title."

	addStatusToArchive(ctx,s,"UrlLog")

	ctx.reply(s, "UrlLog")
		

def showYouTube(ctx, video_id):
	try:	
		meta = urllib.request.urlopen("http://gdata.youtube.com/feeds/api/videos/%s" % video_id)
		meta = dom.parse(meta) #meta.read()
		return displayMeta(ctx, meta, video_id)
	except urllib.error.HTTPError:
		ctx.reply("Invalid youtube URL", "YouTube")
		return

def showTwitter(ctx, tweet_id):
	try:	
		data = urllib.request.urlopen("https://api.twitter.com/1/statuses/show/%s.xml" % tweet_id)
		data = dom.parse(data) #data.read()
		return displayTweet(ctx, data, tweet_id)
	except urllib.error.HTTPError:
		ctx.reply("Invalid twitter URL", "Twitter")
		return

# ---------------------------------------
#       Lookup Functions
# ---------------------------------------

def xmlText(parent, name):
	elem = xmlChild(parent, name)
	if elem is None:
		return None
	return elem.firstChild.data

def xmlChild(parent, name):
	elems = parent.getElementsByTagName(name)
	if len(elems) > 0:
		return elems[0]
	return None

def displayMeta(ctx, data, vid):
	"""Displays a single youtube video result, given the xml node"""
	
	s = ""
	s += "Title: %s " % data.getElementsByTagName("title")[0].firstChild.data
	s += " • By: %s"  % data.getElementsByTagName("author")[0].getElementsByTagName("name")[0].firstChild.data

	showRest = True

	r = data.getElementsByTagName("yt:state")
	if len(r):
		r = r[0]
		if r.getAttribute("name") == "restricted":
			showRest = r.getAttribute("reasonCode") == "limitedSyndication"
			if showRest:
				s += " • Syndication Limited."
			else:
				s += " • Video is unavailable: %s" % r.firstChild.data

	if showRest:
		s += " • Length: %s" % prettyTime(data.getElementsByTagName("yt:duration")[0].getAttribute("seconds"))
		s += " • View Count: %s" % prettyNumber(data.getElementsByTagName("yt:statistics")[0].getAttribute("viewCount"))

		r = data.getElementsByTagName("gd:rating")
		if len(r):
			r = r[0]
			s += " • Average Rating: %1.2f/5 over %s people" % (
				float(r.getAttribute("average")),
				prettyNumber(r.getAttribute("numRaters"))
				)
		else:
			s += " • No ratings"
	
	s += " • http://youtu.be/%s" % vid
	addStatusToArchive(ctx, s, "YouTube")
	ctx.reply(s, "YouTube")

def displayTweet(ctx, data, tweet_id):
	s = "Tweet: "

	retweeted = xmlChild(data, "retweeted_status")
	if retweeted is not None:
		s += "RT @%s %s" % ( xmlText(retweeted, "screen_name"), xmlText(retweeted, "text"))
	else:
		s += xmlText(data, "text")
	
	user = xmlChild(data, "user")

	s += " • Tweeted by: @%s ( %s )" % ( xmlText(user, "screen_name"), xmlText(user, "name"))
	if retweeted is not None:
		s += " • Original retweeted %s times" % xmlText(retweeted, "retweet_count")
	else:
		s += " • Retweets: %s" % xmlText(data, "retweet_count")

	addStatusToArchive(ctx, s, "Twitter")
	ctx.reply(s, "Twitter")

class LookupThread(threading.Thread):
	def __init__(self, ctx, msg):
		threading.Thread.__init__(self, name="Lookup Thread")
		self.ctx = ctx
		self.msg = msg

	def run(self):
		for m in genRegEx.finditer(self.msg):
			showTitle(self.ctx, m.group(0))



def onLoad():
	@hook("message")
	def message_hook(ctx, message):
		t = LookupThread(ctx, message)
		t.start()

	@command("urllog")
	def log_cmd(ctx, cmd, arg):
		outputStatusArchive(ctx)
