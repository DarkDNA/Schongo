# coding=utf-8
"""
Named for Tachikoma the bot in irc.quickfox.net/#subnova created by _3of9
It spams random blurbs and twitter posts all the time
Its purpose here is to spit out rss feed updates
"""
import xml.dom.minidom as dom
import urllib.request
import re
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1.1",
	"Dependencies": [
		"_persist",
		"_timer"
	]
}

__persist__ = [ "feeds", "lastTitles", "feedData" ]
feeds = {}
feedData = {} #stores data on each feed feed : [name, network, channel]
lastTitles = {}

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    p1 = re.compile(r'[[.*?]]')
    htmlRemoved = p.sub('', data)
    return p1.sub('',htmlRemoved)
    
def formatDesc(fullDesc):
	stepOne = re.sub('<img.*alt="([^"]+)".* />', '[\\1]', fullDesc)# get just the alt
	#words = stepOne.split(' ')
	finalDesc = remove_html_tags(stepOne) #' '.join(words[:(len(words) / 2)]))
	if len(finalDesc) > 350:
		finalDesc = finalDesc[:350].replace('\n','')
	finalDesc = '\"%s...\"' % finalDesc
	return finalDesc
	
def sendUpdateToIRC(feed, xml, title):
	dataList = feedData[feed]
	ctx = IrcContext(dataList[1], dataList[2], None)
	link = xml.getElementsByTagName("link")[1].firstChild.data
	desc = formatDesc(xml.getElementsByTagName('description')[1].firstChild.data)
	ctx.reply('New post: %s • %s • %s' % (title, link, desc), dataList[0])
	lastTitles[feed] = title

def onLoad():
	
	@timer(15,True)#update every 5 minutes #DEBUG check timer, set to 15sec
	def update_timer():#timer event
		feedList = feeds.values()
		for feed in feedList:
			if feed is not None:
				site = urllib.request.urlopen(feed)
				xml = dom.parse(site)
				title = xml.getElementsByTagName("title")[1].firstChild.data
				
				if title != lastTitles[feed]:
					sendUpdateToIRC(feed, xml, title)
		return True
#	@command("feed",1,3)

	parent_cmd("feed")


	@command("feed add", 2, 2)
	def feed_add(ctx, cmd, arg, name, feed, *args):
		"""feed add <feed name> <feed url>\nAdd a feed to monitor"""
		if name not in feeds:
			feeds[name] = feed
			feedData[feed] = [name, ctx.irc.network, ctx.chan]
			lastTitles[feed] = ""
			ctx.reply("Added Feed : %s" % name, "Tachikoma")
		else:
			ctx.error("Feed by that name already exists")

	@command("feed force", 1, 1)
	def feed_force(ctx, cmd, arg, name, *args):
		"""feed force <feed name>\nForce the given feed to be updated"""
		if name in feeds:
			feed = feeds[name]
			site = urllib.request.urlopen(feed)
			xml = dom.parse(site)
			title = xml.getElementsByTagName("title")[1].firstChild.data
			sendUpdateToIRC(feed, xml, title)
		else:
			ctx.error("No such feed `%s'" % name)

	@command("feed remove", 1, 1)
	def feed_remove(ctx, cmd, arg, name, *args):
		"""feed remove <feed name>\nRemove the given feed"""
		if name in feeds:
			feed = feeds[name]
			del feedData[feed]
			del feeds[name]
			del lastTitles[feed]
			ctx.reply("Deleted: %s" % name, "Tachikoma")
		else:
			ctx.error("Error deleting Feed: name error")

	@command("feed clear", 0, 0)
	def feed_clear(ctx, cmd, arg, *args):
		"""feed clear\nClear the monitor of all feeds"""
		ctx.reply("Clearing Feeds", "Tachikoma")
		feeds.clear()
		feedData.clear()
		lastTitles.clear()
		ctx.reply("Clearing feeds complete", "Tachikoma")

	@command("feed list", 0, 0)
	def feed_list(ctx, cmd, arg, *args):
		"""feed list\nReturn a list of all stored feeds"""
		for name in feeds:
			feed = feeds[name]
			ctx.reply("%s: %s" % (name, feed), "Tachikoma")
	
	@hook("module_load")
	def timer_start(ctx):
		update_timer.start()
	
	@hook("module_unload")
	def timer_stop(ctx):
		update_timer.stop()
