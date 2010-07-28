"""
Named for Tachikoma the bot in irc.quickfox.net/#subnova created by _3of9
It spams random blurbs and twitter posts all the time
Its purpose here is to spit out rss feed updates
"""
import xml.dom.minidom as dom
import urllib2
import re
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1",
	"Dependencies": []
}

__persist__ = [ "feeds", "lastTitles", "feedData" ]
feeds = {}
feedData = {} #stores data on each feed feed : [name, network, channel]
lastTitles = {}

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
    
def formatDesc(fullDesc):
	stepOne = re.sub('<img.*alt="([^"]+)".* />', '\\1', fullDesc)# get just the alt
	words = stepOne.split(' ')
	finalDesc = remove_html_tags(' '.join(words[:(len(words) / 2)]))
	if len(finalDesc) > 350:
		finalDesc = finalDesc[:350].replace('\n','')
	finalDesc = '\"%s...\"' % finalDesc
	return finalDesc
def onLoad():
	
	@timer(300,True)#update every 5 minutes
	def update_timer(ctx):#timer event
		feedList = feeds.values()
		for feed in feedList:
			if feed is not None:
				site = urllib2.urlopen(feed)
				xml = dom.parse(site)
				title = xml.getElementsByTagName("title")[1].firstChild.data
				
				if title != lastTitles[feed]:
					dataList = feedData[feed]
					ctx = IrcContext(dataList[1], dataList[2], "CurseYouCatFace")
					link = xml.getElementsByTagName("link")[1].firstChild.data
					desc = formatDesc(xml.getElementsByTagName('description')[1].firstChild.data)
					ctx.reply("New post: %s | %s | %s" % (title, link, desc), dataList[0])
					lastTitles[feed] = title
	
	@command("feed",1,3)
	def Rss(ctx, cmd, arg, *args):
	
		if args[0] == "add":#add command for adding feeds
			#add a feed to the module
			if args[1] is not None:
				name = args[1]
				if args[2] is not None:
					feed = args[2]
					#time to add the feed
					if not feeds.has_key(name):
						feeds[name] = feed
						feedData[feed] = [name, ctx.irc.network, ctx.chan]
						lastTitles[feed] = ""
						ctx.reply("Added Feed : %s" % name, "Tachikoma")
					else:
						ctx.error("Feed by that name already exists")
				else:
					ctx.error("Need a rss url")
			else:
				ctx.error("Feed requires a name")
				
		if args[0] == "force":#force update command
			name = args[1]
			if name is not None and feeds.has_key(name):
				feed = feeds[name]
				if feed is not None:
					site = urllib2.urlopen(feed)
					xml = dom.parse(site)
					title = xml.getElementsByTagName("title")[1].firstChild.data
					
					link = xml.getElementsByTagName("link")[1].firstChild.data
					desc = formatDesc(xml.getElementsByTagName('description')[1].firstChild.data)
					ctx.reply("New post: %s | %s | %s" % (title, link, desc), name)
					lastTitles[feed] = title
					
		if args[0] == "remove":#remove command for removing feeds
			name = args[1]
			if name is not None and feeds.has_key(name):
				feed = feeds[name]
				del feedNames[feed]
				del feeds[name]
				del lastTitles[feed]
				ctx.reply("Deleted: %s" % name, "Tachikoma")
			else:
				ctx.error("Error deleting Feed: name error")
				
		if args[0] == "clear": #clear all stored feeds
			ctx.reply("Clearing Feeds", "Tachikoma")
			feeds.clear()
			feedData.clear()
			lastTitles.clear()
			ctx.reply("Clearing feeds complete", "Tachikoma")
			
		if args[0] == "list":#list all stored feeds
			for name in feeds:
				feed = feeds[name]
				ctx.reply("%s: %s" % (name, feed), "Tachikoma")
				
	@hook('module_load')#used to start the timer and load it with a fake ctx in order to make it work
	def hook_modload(modName, modObject):
		if modName == 'tachi':
			dummyCTX = IrcContext("DarkDna","#stoopid", "catface")
			update_timer.start(dummyCTX)

		