"""
Adds a interface with name2key for Second Life
"""


import urllib2
import urllib

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1",
	"Dependencies": []
}
n2kURL = 'http://name2key.alpha-fox.com/?name=%s'

def onLoad():
	@command(["name2key", "n2k"], 2, 2)
	def n2k(ctx, cmd, arg, *args):
		firstName = args[0]
		lastName = args[1]
		combined = '%s %s' % (firstName, lastName)
		response = urllib2.urlopen(n2kURL % urllib.quote(combined))
		key = response.read()
		reply = ''
		if key == '00000000-0000-0000-0000-000000000000':
			reply = 'Key not found'
		else:
			reply = "%s %s\'s key is %s" % (firstName, lastName, key)
		
		ctx.reply(reply, "Name2key")
		
	