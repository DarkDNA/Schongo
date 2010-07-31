# coding=utf-8
""" Interface with the Stack Exchange API Current only supports stackoverflow others may follow""" 

import urllib2
import json
import gzip


from StringIO import StringIO
from _utils import prettyNumber

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

baseURL = "http://%s.%s.com%s"
apiURL = baseURL % ('api','stackoverflow','/1.0/%s')
qURL = baseURL % ('www','stackoverflow','/%s/%s') 

def jsonLoad(fp):
	if hasattr(json, "load"):
		# Proper json module 2.6+
		return json.load(fp)
	elif hasattr(json, "read"):
		# python-support hack
		return json.read(fp.read())
	else:
		# Quick hack for now. :(
		return {
		"total": "0"
	}

def onLoad():
	@command("so",1)
	def search(ctx, cmd, arg, *args):
		thingy = ";".join(args)

		bunnies = 'search?tagged=%s&pagesize=5' % thingy
		searchURL = apiURL % bunnies

		urlObject = urllib2.urlopen(searchURL)
		urlObject = StringIO(urlObject.read()) # Ugly hack because we can't .read() from the gzip otherwise
		urlObject = gzip.GzipFile(fileobj=urlObject) # Stack Overflow compresseses


		decoded = jsonLoad(urlObject)

		results = decoded["total"]

		if results > 0:
			res = min(results, 5)
			ctx.reply("Results 1-%d of %s" % (res, prettyNumber(results)), "StackOverflow")
		else:
			ctx.reply("No results for your query", "StackOverflow")
		

		for q in decoded['questions']:
			title = q['title']
			commentURL = q['question_comments_url'].split('/')
			questionURL = qURL % (commentURL[1], commentURL[2])
			ctx.reply(u'%s • %s' % (title, questionURL), 'StackOverflow')
				
			
