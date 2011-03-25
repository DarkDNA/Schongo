# coding=utf-8
"""Sniffs URLs and shows the title for them, with special detection for sniffing youtube URLs"""

import urllib2
import xml.dom.minidom as dom
import re
from _utils import prettyNumber, prettyTime

READ_SIZE = 32000;

__info__ = {
	"Author": "Selig Arkin",
	"Version": "1.0b",
	"Dependencies": []
}


ytRegEx = re.compile(r"(https?://)?(www\.)?youtu(be\.com/watch\?v=|\.be/)([^& ]+)")
genRegEx = re.compile(r"https?://([^ ]+)")
titleRegEx = re.compile(r"<title>(.+)</title>")


def showTitle(ctx, url):
	ytMatch = ytRegEx.match(url)
	if ytMatch:
		showYouTube(ctx, ytMatch.group(4))
		return

	u = urllib2.urlopen(url)
	stuff = u.read(READ_SIZE)
	newurl = u.url
	u.close()

	# Look again after reading it in, to see if it is a shortened youtube url.

	m = ytRegEx.match(newurl)
	if m is not None:
		showYouTube(ctx, m.group(4))
		return

	s = u"Url: %s" % url

	if newurl != url:
		s += u" • Redirects to: %s" % newurl

	title = titleRegEx.match(stuff)
	if title is not None:
		s += u" • Title: %s" % title.group(1)
	else:
		s += u" • Couldn't find Title"

	ctx.reply(s, "UrlLog")
		

def showYouTube(ctx, video_id):
	
	meta = urllib2.urlopen("http://gdata.youtube.com/feeds/api/videos/%s" % video_id)
	meta = dom.parse(meta) #meta.read()
	
	return displayMeta(ctx, meta, video_id)

def displayMeta(ctx, data, vid):
	"""Displays a single youtube video result, given the xml node"""
	
	s = u""
	s += u"Title: %s " % data.getElementsByTagName("title")[0].firstChild.data
	s += u" • By: %s"  % data.getElementsByTagName("author")[0].getElementsByTagName("name")[0].firstChild.data
	s += u" • Length: %s" % prettyTime(data.getElementsByTagName("yt:duration")[0].getAttribute("seconds"))
	s += u" • View Count: %s" % prettyNumber(data.getElementsByTagName("yt:statistics")[0].getAttribute("viewCount"))

	r = data.getElementsByTagName("gd:rating")
	if len(r):
		r = r[0]
		s += u" • Average Rating: %1.2f/5 over %s people" % (
			float(r.getAttribute("average")),
			prettyNumber(r.getAttribute("numRaters"))
			)
	else:
		s += u" • No ratings"
	
	s += u" • http://youtu.be/%s" % vid
	#addStatusToArchive(ctx, s)
	ctx.reply(s, "YouTube")

def onLoad():
	@hook("message")
	def message_hook(ctx, message):
		for m in genRegEx.finditer(message):
			showTitle(ctx, m.group(0))
