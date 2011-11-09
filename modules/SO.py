# coding=utf-8
""" Interface with the Stack Exchange API Current only supports stackoverflow others may follow""" 

from urllib import request
import json
import gzip


from io import StringIO
from modules._utils import prettyNumber

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1.0",
	"Dependencies": []
}

baseURL = "http://{}.{}.com{}"
apiURL = baseURL.format('api','stackoverflow','/1.0/{}')
qURL = baseURL.format('www','stackoverflow','/{}/{}') 

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
		"""so <tag1> <tag2> <etc>\nSearch through stackoverflow for the given tags"""
		thingy = ";".join(args)

		bunnies = 'search?tagged={}&pagesize=3'.format(thingy)
		searchURL = apiURL.format(bunnies)

		urlObject = request.urlopen(searchURL)
		urlObject = StringIO(str(urlObject.read())) # Ugly hack because we can't .read() from the gzip otherwise
		urlObject = gzip.GzipFile(fileobj=urlObject) # Stack Overflow compresseses


		decoded = jsonLoad(urlObject)

		results = decoded["total"]

		if results > 0:
			res = min(results, 3)
			ctx.reply("Results 1-{} of {}".format(res, prettyNumber(results)), "StackOverflow")
		else:
			ctx.reply("No results for your query", "StackOverflow")
		

		for q in decoded['questions']:
			title = q['title']
			questionURL = qURL.format('questions', q['question_id'])
			ctx.reply('{} • {}'.format(title, questionURL), 'StackOverflow')
				
			
