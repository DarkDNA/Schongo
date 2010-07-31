# coding=utf-8
""" Interface with the Stack Exchange API Current only supports stackoverflow others may follow""" 

from __future__ import with_statement
import urllib2
import json
from StringIO import StringIO
import gzip

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}
baseURL = "http://%s.%s.com%s"
apiURL = baseURL % ('api','stackoverflow','/1.0/%s')
qURL = baseURL % ('www','stackoverflow','/%s/%s') 

def decompress(data):
	compressedStream = StringIO(data)
	gziped = gzip.GzipFile(fileobj=compressedStream)
	decompressed = gziped.read()
	return StringIO(decompressed)

def onLoad():
	@command("so")
	def search(ctx, cmd, arg, *args):
		args = arg.split(' ')
		thingy = ";".join(args)
		print thingy
		bunnies = 'search?tagged=%s' % thingy
		searchURL = apiURL % bunnies
		#print searchURL
		urlObject = urllib2.urlopen(searchURL)
		jsonData = decompress(urlObject.read())
		decoded = json.load(jsonData)
		#print decoded
		questions = decoded['questions']
		title = ''
		commentURL = None
		questionURL = ''
		ircResponse = ''
		for q in questions[:5]:
			title = q.get('title')
			commentURL = q.get('question_comments_url').split('/')
			questionURL = qURL % (commentURL[1], commentURL[2])
			ircResponse = u'%s • %s' % (title, questionURL)
			ctx.reply(ircResponse, 'StackOverFlow')
				
			
