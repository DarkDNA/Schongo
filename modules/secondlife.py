# coding=utf-8
"""
Adds a interface with various SL APIs Name2Key and key2name are currently broken due to drama on the providers side
A new service will be developed when I feel like it
"""

import urllib2
import urllib
import xml.dom.minidom as dom

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

n2kURL = 'http://name2key.alpha-fox.com/?name=%s'
k2nURL = 'http://key2name.alpha-fox.com/?key=%s'

slXMLFeed = 'http://secondlife.com/xmlhttp/secondlife.php'

lastStatus = ''

def onLoad():
	@command(["name2key", "n2k"], 2, 2)
	def n2k(ctx, cmd, arg, *args):
		"""Name2Key <UUID>\nlooks up the Secondlife UUID and returns a name"""
		response = urllib2.urlopen(n2kURL % urllib.quote(arg))
		key = response.read()
		reply = ''
		if key == '00000000-0000-0000-0000-000000000000':
			reply = 'Key not found'
		else:
			reply = "%s\'s key is %s" % (arg, key)
		
		ctx.reply(reply, "Name2Key")
		
	@command("slstatus")
	def statusUpdate(ctx, cmd, arg, *args):
		"""slstatus\nRetrieves the current status of the Second Life Grid"""
		request = urllib2.urlopen(slXMLFeed)
		xml = dom.parse(request)
		status = xml.getElementsByTagName('status')[0].firstChild.data
		signups = xml.getElementsByTagName('signups')[0].firstChild.data
		inworld = xml.getElementsByTagName('inworld')[0].firstChild.data
		
		xml.unlink();
		
		ctx.reply("Current status is %s • Total Users: %s • Users Online: %s" % 
			( status.capitalize(), signups, inworld ), "Second Life")
