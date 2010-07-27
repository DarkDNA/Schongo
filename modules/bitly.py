"""Interfaces with the bit.ly URL shortening service

Adds the 'bitly' command.
Also adds a sniffer to find bit.ly urls and expand them"""

import urllib2
import urllib
import re


__info__ = {
	"Author": "Wil Hall",
	"Version": "1.0",
	"Dependencies": []
}


def getLongUrl(short):
	try:
		request = urllib2.Request(short)
		opener = urllib2.build_opener()
		response = opener.open(request)
		url = response.url
		return url
	except urllib2.URLError:
		return None

def onLoad():
	@command('bitly', 1, 1)
	def bitly_cmd(ctx, cmd, arg, *args):
		"""bitly <long-url>
Condences <long-url> using the bit.ly url shortening service"""
		try:
			cmdurl = "http://api.bit.ly/v3/shorten?login=wilatkathbot3&apiKey=R_8fa4afa5dda9ae6cab93896eaf04c8de&longUrl=%s&format=txt" % urllib.quote(args[0], ':/').strip().rstrip()
			response = urllib2.urlopen(cmdurl)
			url = response.read()
			ctx.reply(u"`Bbit.ly URL:`B %s" % url, 'bitly')
		except urllib2.URLError:
			ctx.error("Error processing your request, please try again later")


	@hook("message")
	def message_hook(ctx, msg):
		for m in re.finditer("http://(bit\\.ly|j\\.mp)/([a-zA-Z0-9]+)", msg):
			short = m.group(0)
			long = getLongUrl(short)
			if long:
				ctx.reply("`BBit.ly url:`B %s - `BLong:`B %s" % (short, long), "bitly")
			else:
				ctx.reply("`BBit.ly url:`B %s is invalid." % short, "bitly")
