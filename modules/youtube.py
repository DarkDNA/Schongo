# coding=utf-8


"""Implements various commands to interact with YouTube, and a meta information grabber"""



import urllib2
import urllib
import xml.dom.minidom as dom
import re
from _utils import prettyNumber, prettyTime

def YoutubeMeta(ctx, video_id):
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
		s += u" • Average Rating: %1.2f/5" % float(r.getAttribute("average"))
	else:
		s += u" • No ratings"

	s += u" • http://youtu.be/%s" % vid
 
	ctx.reply(s, "YouTube")

# 

ytRegEx = re.compile("http://(www\\.)?youtube.com/watch\\?v=([^&]+)")
ytOtherRegEx = re.compile("video:(.+)")

# And now for something completely different

def onLoad():
	@command("youtube")
	def youtube_cmd(ctx, cmd, arg):
		url = "http://gdata.youtube.com/feeds/api/videos?q=%s&max-results=5&v=2" % urllib.quote(arg)
		r = urllib2.urlopen(url)
		r = dom.parse(r)
			
		results = int(r.getElementsByTagName("openSearch:totalResults")[0].firstChild.data)

		if results > 0:
			res = min(results, 5)
			ctx.reply("Results 1-%d out of %s" % (res, prettyNumber(results)), "YouTube")
		else:
			ctx.reply("No results found for %s" % arg, "YouTube")

		for i in r.getElementsByTagName("entry"):
			vid = i.getElementsByTagName("id")[0].firstChild.data
			vid = vid.split(":")[-1]

			displayMeta(ctx, i, vid)

	@hook("message")
	def message_hook(ctx, message):
		for m in ytRegEx.finditer(message):
			YoutubeMeta(ctx, m.group(2))
		
