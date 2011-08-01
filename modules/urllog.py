# coding=utf-8
"""Sniffs URLs and shows the title for them, with special detection for sniffing youtube URLs"""

import urllib2
import xml.dom.minidom as dom
import re
from _utils import prettyNumber, prettyTime
import threading

archive = dict()


READ_SIZE = 32000;

__info__ = {
	"Author": "Selig Arkin",
	"Version": "1.0b",
	"Dependencies": []
}


ytRegEx = re.compile(r"(https?://)?(www\.)?youtu(be\.com/watch\?v=|\.be/)([^& ]+)")
genRegEx = re.compile(r"https?://([^ ]+)")
titleRegEx = re.compile(r"<title>(.+)</title>")
titleMimes = [ "text/html" ]

def addStatusToArchive(ctx, s, prefix):
	global archive
	chan = ctx.chan
	if archive.has_key(chan):
		archive[chan].insert(0, (prefix,s))
	elif not archive.has_key(chan):
		archive[chan] = list()
		archive[chan].append((prefix,s))

	if len(archive[chan]) > 5:
		archive[chan] = archive[chan][:5]

def outputStatusArchive(ctx):
	global archive
	if archive.has_key(ctx.chan):
		if len(archive[ctx.chan]) > 0:
			[ctx.reply(s[1],s[0]) for s in archive[ctx.chan]]
			
		else:
			ctx.reply("Empty log", "UrlLog")
	else:
		ctx.reply("Empty log", "UrlLog")

def showTitle(ctx, url):
	ytMatch = ytRegEx.match(url)
	if ytMatch:
		showYouTube(ctx, ytMatch.group(4))
		return

	s = u"Url: %s" % url

	try:
		u = urllib2.urlopen(url)
		stuff = u.read(READ_SIZE)
		newurl = u.url
		mime = u.info().gettype()
		u.close()
	except urllib2.HTTPError:
		# Intentionally not adding this to the archive, no point spamming unparsable URLs
		s += u" • Failed to get title: HTTP Error."
		ctx.reply(s, "UrlLog")
		return
	except urllib2.URLError:
		s += u" • Failed to get title: URL Error."
		ctx.reply(s, "UrlLog")
		return

	# Look again after reading it in, to see if it is a shortened youtube url.

	m = ytRegEx.match(newurl)
	if m is not None:
		showYouTube(ctx, m.group(4))
		return


	if newurl != url:
		s += u" • Redirects to: %s" % newurl

	if mime not in titleMimes:
<<<<<<< HEAD
		s += u" • MIME type: %s" % mime
=======
		s += u" • MIME: %s" % mime
>>>>>>> 503fde1151874a14c4ffbab919c2c0bbf13b11fd

	titleSearch = titleRegEx.search(stuff)
	if titleSearch is not None:
		s += u" • Title: %s" % titleSearch.group(1)
	elif mime in titleMimes:
		s += u" • Could not find title."

	addStatusToArchive(ctx,s,"UrlLog")

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

	showRest = True

	r = data.getElementsByTagName("yt:state")
	if len(r):
		r = r[0]
		if r.getAttribute("name") == "restricted":
			showRest = r.getAttribute("reasonCode") == "limitedSyndication"
			if showRest:
				s += u" • Syndication Limited."
			else:
				s += u" • Video is unavailable: %s" % r.firstChild.data

	if showRest:
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
	addStatusToArchive(ctx, s, "YouTube")
	ctx.reply(s, "YouTube")


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
