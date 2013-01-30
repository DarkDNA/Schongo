# coding=utf-8
"""Implements various commands to interact with YouTube, and a meta information grabber"""

import urllib.request, urllib.parse
import xml.dom.minidom as dom
import re
from modules._utils import prettyNumber, prettyTime

def YoutubeMeta(ctx, video_id):
	meta = urllib.request.urlopen("http://gdata.youtube.com/feeds/api/videos/%s" % video_id)
	meta = dom.parse(meta) #meta.read()
	
	return displayMeta(ctx, meta, video_id)

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
	ctx.reply(s, "YouTube")

# 

ytOtherRegEx = re.compile("video:(.+)")

# And now for something completely different

def onLoad():
	@command("youtube")
	def youtube_cmd(ctx, cmd, arg):
		"""youtube <search string>
Searches youtube for the given search string"""
		url = "http://gdata.youtube.com/feeds/api/videos?q=%s&max-results=3&v=2" % urllib.parse.quote(arg)
		r = urllib.request.urlopen(url)
		r = dom.parse(r)
			
		results = int(r.getElementsByTagName("openSearch:totalResults")[0].firstChild.data)

		if results > 0:
			res = min(results, 3)
			ctx.reply("Results 1-%d out of %s" % (res, prettyNumber(results)), "YouTube")
		else:
			ctx.reply("No results found for %s" % arg, "YouTube")

		for i in r.getElementsByTagName("entry"):
			vid = i.getElementsByTagName("id")[0].firstChild.data
			vid = vid.split(":")[-1]

			displayMeta(ctx, i, vid)
