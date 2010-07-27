"""
Named for tachikoma the bot in irc.quickfox.net/#subnova created by _3of9
It spams random blurbs and twitter posts all the time
Its purpose here is to spit out rss feed updates
"""
import xml.dom.minidom as dom
import urllib2
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

__persist__ = [ "feeds" ]
feeds = {}
feedNames = {}
lastTitles = {}
def onLoad():
	
	@timer(300,True)#update every 5 minutes
	def update(ctx):
		rssXml = ''
		for feed in feeds:
			if feed is not None:
				site = urllib2.urlopen(feed)
				xml = dom.parse(site)
				title = xml.getElementsByTagName("title")[1].firstChild.data
				if title is not lastTitles[feed]:
					link = xml.getElementsByTagName("link")[1].firstChild.data
					ctx.reply("New post: %s" % link, feedName[feed])
					lastTitles[feed] = title
	
	@command("feed",2,3)
	def addRss(ctx, cmd, arg, *args):
		if args[0] == "add":
			#add a feed to the module
			if args[1] is not None:
				name = args[1]
				if args[2] is not None:
					feed = args[2]
					#time to add the feed
					if not feeds.has_key(name):
						feeds[name] = feed
						feedNames[feed] = name
						lastTitles[feed] = ""
						ctx.reply("Added Feed: %s" % name, "Tachikoma")
					else:
						ctx.error("Feed by that name already exists")
				else:
					ctx.error("Need a rss url")
			else:
				ctx.error("Feed requires a name")
		if args[0] == "force":
			name = args[1]
			if name is not None and feeds.has_key(name):
				feed = feeds[name]
				if feed is not None:
					site = urllib2.urlopen(feed)
					xml = dom.parse(site)
					title = xml.getElementsByTagName("title")[1].firstChild.data
					
					link = xml.getElementsByTagName("link")[1].firstChild.data
					
					ctx.reply("New post: %s" % link, name)
					lastTitles[feed] = title
		if args[0] == "remove":
			name = args[1]
			if name is not None and feeds.has_key(name):
				feed = feeds[name]
				del feedNames[feed]
				del feeds[name]
				del lastTitles[feed]
				ctx.reply("Deleted: %s" % name, "Tachikoma")
			else:
				ctx.error("Error deleting Feed: name error")
		if args[0] == "clear":
			ctx.reply("Clearing Feeds", "Tachikoma")
			feeds.clear()
			feedNames.clear()
			lastTitles.clear()
			ctx.reply("Clearing feeds complete", "Tachikoma")
			
				

		