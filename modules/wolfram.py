"""Querys Wolfram|Alpha and displays the results.

** Warning: Not all data is currently displayable **
"""

import urllib2
import urllib
import xml.dom.minidom as dom

def Format_Pod(data):
	result = []

	for i in data.getElementsByTagName("subpod"):
		d = i.getElementsByTagName("plaintext")

		if not len(d):
			continue
		
		d = d[0]

		dat = ""

		if d.hasAttribute("title") and d.getAttribute("title") != "":
			dat = d.getAttribute("title") + ": "

		dat += d.firstChild.data

		result.append(dat)

	title = "Result"

	if data.hasAttribute("title") and data.getAttribute("title") != "":
		title = data.getAttribute("title")
	
	return "%s: %s" % (title, " / ".join(result))

def onLoad():
	@command("wolfram")
	def cmd_wolfram(ctx, cmd, arg):
		resp = urllib2.urlopen("http://api.wolframalpha.com/v2/query?input=%s&format=plaintext&appid=%s" % (urllib.quote(arg.encode("utf-8")), cfg.get("key")))

		xml = dom.parse(resp)

		i = 0

		for pod in xml.getElementsByTagName("pod"):
			ctx.reply(Format_Pod(pod), "W|A", parse=False)
			i += 1

			if i > 3:
				ctx.reply(u"More can be obtained from the website.", "W|A")
				break

		if i == 0:
			ctx.reply("No valid response was received.", "W|A")
