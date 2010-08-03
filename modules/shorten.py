# coding=utf-8
"""Interfaces with shortening services, and expands shortened urls

Adds the 'shorten' command, currently hard-coded to use bit.ly
Also adds a sniffer to find short urls and expand them

Original Module by Wil Hall - Hacked to death by Selig Arkin"""

import urllib2
import urllib
import re


__info__ = {
	"Author": "Wil Hall, Selig Arkin",
	"Version": "1.1",
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

## TODO: Add more services!
shorten = {
	"bitly": "http://api.bit.ly/v3/shorten?login=wilatkathbot3&apiKey=R_8fa4afa5dda9ae6cab93896eaf04c8de&longUrl=%s&format=txt",
	"jmp": "http://api.bit.ly/v3/shorten?login=wilatkathbot3&apiKey=R_8fa4afa5dda9ae6cab93896eaf04c8de&longUrl=%s&format=txt&domain=j.mp",
}


def onLoad():
	@command('shorten', 1, 2)
	def bitly_cmd(ctx, cmd, arg, *args):
		"""shorten [service] <long-url>
Condences <long-url> using the given service (currently defaults to bit.ly)"""
		if arg.startswith("http://"):
			service = "bitly"
			url = arg
		else:
			parts = arg.split(' ', 1)
			service = parts[0]
			url = parts[1]

		if not shorten.has_key(service):
			ctx.error("Unknown service %s" % service)

		try:
			if isinstance(shorten[service], str):
				cmdurl = shorten[service] % url
				response = urllib2.urlopen(cmdurl)
				short = response.read().strip()
			else:
				short = shorten[service](url)

			slen = len(short)
			llen = len(url)
			ctx.reply(u"`BShort URL:`B %s • Long: %d • Short: %d • Compression: TODO%%" % (short, llen, slen), 'shorten')
		except urllib2.URLError:
			ctx.error("Error processing your request, please try again later")


	@hook("message")
	def message_hook(ctx, msg):
		for m in re.finditer(r"http://(bit\.ly|j\.mp|s[nl]\.im|tinyurl\.com|goo.gl|is\.gd|wp\.me|to\.ly|tr\.im|tiny\.(cc|pl)|no\.to|om\.ly|ow\.ly)/([^ ]+)", msg):
			short = m.group(0)
			long = getLongUrl(short)
			if long:
				ctx.reply(u"`BShort url:`B %s • `BLong:`B %s" % (short, long), "shorten")
			else:
				ctx.reply("`BShort url:`B %s is invalid." % short, "shorten")
