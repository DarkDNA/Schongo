"""
Adds a interface with various SL APIs
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
		
	
	@timer(180,True)#update timer for the Sl status feed
	def slStatus_timer(ctx):
		request = urllib2.urlopen(slXMLFeed)
		xml = dom.parse(request)
		status = xml.getElementsByTagName('status')[0].firstChild.data
		if status is not None and status is not lastStatus:
			if status == "ONLINE":
				ctx.reply("SecondLife Grid is Online", "SL-Status")
			else:
				ctx.reply("SecondLife Grid is Offline", "SL-Status")
			lastStatus = status
			
	@command("slStatus") # for now it starts the timer and does an explicit update of all data
	def statusUpdate(ctx, cmd, arg, *args):
		slStatus_timer.start(ctx)
		request = urllib2.urlopen(slXMLFeed)
		xml = dom.parse(request)
		status = xml.getElementsByTagName('status')[0].firstChild.data
		print status
		if status == "ONLINE":
			ctx.reply("SecondLife Grid is Online", "Second Life")
		else:				
			ctx.reply("SecondLife Grid is Offline", "Second Life")
		lastStatus = status
			
	@command("slUsers")
	def getSlUsers(ctx, cmd, arg, *args):
		request = urllib2.urlopen(slXMLFeed)
		xml = dom.parse(request)
		users = xml.getElementsByTagName('signups')[0].firstChild.data
		ctx.reply("Users registered for Second Life: %s" % users, "Second Life")
		
	@command("online")
	def usersOnline(ctx, cmd, arg, *args):
		request = urllib2.urlopen(slXMLFeed)
		xml = dom.parse(request)
		online = xml.getElementsByTagName('inworld')[0].firstChild.data
		ctx.reply("Users currently logged into Second Life: %s" % online, "Second Life")
