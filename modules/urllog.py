# -*- coding: utf-8 -*-
"""Sniffs URLs and shows the title for them, with special detection for sniffing youtube URLs"""

import urllib.request
import urllib.error
import urllib.parse
import xml.dom.minidom as dom
import re
from modules._utils import prettyNumber, prettyTime, unescapeHtml
import threading

archive = dict()


READ_SIZE = 32000

__info__ = {
	"Author": "Amanda Cameron",
	"Version": "1.0b",
	"Dependencies": []
}


ytRegEx = re.compile(r"(https?://)?(www\.)?youtu(be\.com/watch\?[^ ]*v=|\.be/)([^& ]+)")
twitterRegEx = re.compile(r"(https?://)?twitter.com/(#!)?[a-zA-Z0-9_]+/status/(\d+)")

genRegEx = re.compile(r"https?://([^ ]+)")
titleRegEx = re.compile(r"<title[^>]*>*([^<]+)</title>", re.IGNORECASE)
titleMimes = [ "text/html", "application/xhtml+xml" ]

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
			ctx.reply("Empty log", "URL")
	else:
		ctx.reply("Empty log", "URL")

def showTitle(ctx, url):
	ytMatch = ytRegEx.match(url)
	if ytMatch:
		showYouTube(ctx, ytMatch.group(4))
		return

	twitMatch = twitterRegEx.match(url)
	if twitMatch:
		showTwitter(ctx, twitMatch.group(3))
		return

	
	s = pretty_url(url)

	encoding = None
	
	try:
		u = get_url(url)
		stuff = u.read(READ_SIZE)
		newurl = u.url
		mime = u.info().get_content_type()
		encoding = u.info().get_param("charset")
		u.close()
	except urllib.error.HTTPError as e:
		# Intentionally not adding this to the archive, no point spamming unparsable URLs
		s += " • Failed to get information, HTTP Error: %d." % e.code
		ctx.reply(s, "URL")
		return
	except urllib.error.URLError as e:
		s += " • Failed to get information: URL Error: %s." % e.reason
		ctx.reply(s, "URL")
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

	if pretty_url(newurl) != pretty_url(url):
		s += " • Redirects to: %s" % pretty_url(newurl)

	if mime not in titleMimes:
		s += " • MIME type: %s" % mime

	if mime in titleMimes:
		stuff = stuff.decode(encoding)

		titleSearch = titleRegEx.search(stuff)
		if titleSearch is not None:
			title = titleSearch.group(1)
			title = title.replace("\n", "").replace("\r", "").replace("\t", " ")
			title = title.strip()

			s += " • Title: %s" % unescapeHtml(title)
		else:
			s += " • Could not find title."

	addStatusToArchive(ctx, s, "URL")

	ctx.reply(s, "URL")
		

def showYouTube(ctx, video_id):
	try:	
		meta = get_url("http://gdata.youtube.com/feeds/api/videos/%s" % video_id)
		meta = dom.parse(meta) #meta.read()
		return displayMeta(ctx, meta, video_id)
	except urllib.error.HTTPError:
		ctx.reply("Invalid youtube URL", "YouTube")
		return

def showTwitter(ctx, tweet_id):
	try:	
		data = get_url("https://api.twitter.com/1/statuses/show/%s.xml" % tweet_id)
		data = dom.parse(data) #data.read()
		return displayTweet(ctx, data, tweet_id)
	except urllib.error.HTTPError:
		ctx.reply("Invalid twitter URL", "Twitter")
		return


# ---------------------------------------
#       Pretty Pretty
# ---------------------------------------

def pretty_url(url):
	o = urllib.parse.urlparse(url)

	return o.netloc

def pretty_url_old(url):
	if len(url) <= 100:
		return url.replace('tt', 't\x02\x02t')

	o = urllib.parse.urlparse(url)

	s = "%s://%s/" % (o.scheme.replace('tt', 't\x02\x02t'), o.netloc)

	if o.path == '':
		path = []
	else:
		path = o.path.split('/')

	
	if len(path) > 2:
		s += '.../%s' % path[-1]
	elif len(path) == 2:
		s += "%s" % path[1]

	return s

# ---------------------------------------
#       LONG LIVE HYPNOTOAD
# ---------------------------------------

def get_url(url):
	req = urllib.request.Request(url, None, {
		"User-Agent": "Schongo/1.0 (http://darkdna.net/; schongo@darkdna.net)"
	})

	return urllib.request.urlopen(req)


# ---------------------------------------
#       XML Helpers.
# ---------------------------------------


def xmlText(parent, name):
	elem = xmlChild(parent, name)
	if elem is None:
		return None
	return elem.firstChild.data

# This has to get the first child this way because getElementsByTagName does 
# depth-first search, confusing data for the twitter handling
def xmlChild(parent, name):
	for c in parent.childNodes:
		if c.nodeName == name:
			return c
	return None

# ---------------------------------------
#       Lookup Functions
# ---------------------------------------

#TODO: Convert this into using the xml helpers above
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
	
	s += " • https://youtu.be/%s" % vid
	addStatusToArchive(ctx, s, "YouTube")
	ctx.reply(s, "YouTube")

def displayTweet(ctx, data, tweet_id):
	s = "Tweet: "

	data = xmlChild(data, "status")

	retweeted = xmlChild(data, "retweeted_status")
	if retweeted is not None:
		retweeted_user = xmlChild(retweeted, "user")
		s += "RT @%s %s" % ( xmlText(retweeted_user, "screen_name"), xmlText(retweeted, "text"))
	else:
		s += xmlText(data, "text")

	user = xmlChild(data, "user")

	if retweeted:
		maybeRe = "Ret"
	else:
		maybeRe = "T"

	s += " • %sweeted by: @%s ( %s )" % ( maybeRe, xmlText(user, "screen_name"), xmlText(user, "name"))
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
