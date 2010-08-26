# coding=utf-8
"""Looks up information from a MediaWiki wiki - Currently only Wikipedia

Please note that this is still in development and needs some kinks to be worked out still"""

import urllib
import urllib2
import xml.dom.minidom as dom
import re
from _utils import prettyNumber

def openUrl(url):
	r = urllib2.Request(url, headers={
		"User-Agent": "Schongo Bot"})
	return urllib2.urlopen(r)


def onLoad():
	@command(["wikipedia", "wiki"])
	def wikipedia_cmd(ctx, cmd, arg):
		"""wikipedia <search>
Searches through wikipedia for the given search string"""
		o = openUrl(u"http://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s&srwhat=text&srlimit=5&format=xml" % urllib.quote(arg))

		xml = dom.parse(o)
		
		results = int(xml.getElementsByTagName("searchinfo")[0].getAttribute("totalhits"))
		
		if results > 0:
			res = min(results, 5)
			ctx.reply("Results 1-%d out of %s" % (res, prettyNumber(results)), "Wikipedia")
		else:
			ctx.reply(u"No results found for %s" % arg, "Wikipedia")

		for i in xml.getElementsByTagName("p"):
			title = i.getAttribute("title")
			snippet = i.getAttribute("snippet")
			# Hilight the matched parts
			snippet = re.sub('<span class=\'searchmatch\'>(.+?)</span>', u'`B\\1`B', snippet)
			# Clean it up nice and pretty now
			snippet = re.sub('<[^>]+>', u'', snippet)
			snippet = re.sub(' ([.,!?\'])', u'\\1', snippet)
			snippet = snippet.replace('  ', u' ')
			# And then display it. :D
			ctx.reply(u"`B%s`B ( %s ) • %s" % (title, "http://wikipedia.org/wiki/%s" % urllib.quote(title), snippet), "Wikipedia")
