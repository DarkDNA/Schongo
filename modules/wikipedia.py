# coding=utf-8
"""Looks up information from a MediaWiki wiki - Currently only Wikipedia

Please note that this is still in development and needs some kinks to be worked out still"""

import urllib.request
import urllib.parse
import xml.dom.minidom as dom
import re
from modules._utils import prettyNumber

def openUrl(url):
	r = urllib.request.Request(url, headers={
		"User-Agent": "Schongo Bot"})
	return urllib.request.urlopen(r)


def onLoad():
	@command(["wikipedia", "wiki"])
	def wikipedia_cmd(ctx, cmd, arg):
		"""wikipedia <search>
Searches through wikipedia for the given search string"""
		o = openUrl("http://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={}&srwhat=text&srlimit=3&format=xml".format(urllib.parse.quote(arg)))

		xml = dom.parse(o)
		
		results = int(xml.getElementsByTagName("searchinfo")[0].getAttribute("totalhits"))
		
		if results > 0:
			res = min(results, 3)
			ctx.reply("Results 1-{} out of {}".format(res, prettyNumber(results)), "Wikipedia")
		else:
			ctx.reply("No results found for {}".format(arg), "Wikipedia")

		for i in xml.getElementsByTagName("p"):
			title = i.getAttribute("title")
			snippet = i.getAttribute("snippet")
			# Hilight the matched parts
			snippet = re.sub('<span class=\'searchmatch\'>(.+?)</span>', '`B\\1`B', snippet)
			# Clean it up nice and pretty now
			snippet = re.sub('<[^>]+>', '', snippet)
			snippet = re.sub(' ([.,!?\'])', '\\1', snippet)
			snippet = snippet.replace('  ', ' ')
			# And then display it. :D
			ctx.reply("`B{}`B ( {} ) • {}".format(title, "http://wikipedia.org/wiki/{}".format(urllib.parse.quote(title)), snippet), "Wikipedia")
