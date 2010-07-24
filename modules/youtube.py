"""Implements various commands to interact with YouTube, and a meta information grabber"""

import urllib2
import urllib
import xml.dom.minidom as dom
import re

def YoutubeMeta(ctx, video_id):
	meta = urllib2.urlopen("http://gdata.youtube.com/feeds/api/videos/%s" % video_id)
	meta = dom.parse(meta) #meta.read()
	
	return displayMeta(ctx, meta, video_id)

def displayMeta(ctx, data, vid):
	"""Displays a single youtube video result, given the xml node"""

	s = ""
	s += "Title: %s " % data.getElementsByTagName("title")[0].firstChild.data
	s += " - By: %s"  % data.getElementsByTagName("author")[0].getElementsByTagName("name")[0].firstChild.data
	s += " - View Count: %s" % data.getElementsByTagName("yt:statistics")[0].attributes["viewCount"].value
	r = data.getElementsByTagName("gd:rating")
	if len(r):
		r = r[0]
		s += " - Average Rating: %s/5" % r.attributes["average"].value

	s += " - http://youtu.be/%s" % vid
 
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
	
		for i in r.getElementsByTagName("entry"):
			vid = i.getElementsByTagName("id")[0].firstChild.data
			vid = vid.split(":")[-1]

			displayMeta(ctx, i, vid)

	@hook("message")
	def message_hook(ctx, message):
		m = ytRegEx.search(message)
		if m is not None:
			YoutubeMeta(ctx, m.group(2))
		
