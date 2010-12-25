# coding=utf-8
"""
The Santa tracking module for schongo :D
"""

import urllib2
import datetime
from time import time

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": [
		"_timer"
	]
}
chan = ''
net = ''
dataURL = "http://www.noradsanta.org/js/data.js"
lastLoc = ''
def onLoad():

	locList = eval(urllib2.urlopen(dataURL).read().split('= ')[1])

	@timer(60,True)
	def updateTimer():
		global lastLoc

		#currentTotal = (dt.hour * 60) + dt.minute
		currentTotal = (int(time()) - 1293174000) / 60;
		
		for stop in locList:
			t = stop['time'].split(':')
			h = int(t[0])
			m = int(t[1])
			total = (h * 60) + m
			#
			offset = stop['travel_time'].split(":")
			if offset == ['']:
				offset = ['','']
			if offset[0] != '':
				offsetH = int(offset[0])
			else:
				offsetH = 0
			
			if offset[1] != '':
				offsetM = int(offset[1])
			else:
				offsetM = 0
			offsetTotal = (offsetH * 60) + offsetM
			print 'loc: %s\nmin: %s\ncurrent: %s\nmax: %s' % (stop['full_location'], total, currentTotal, (total + offsetTotal))
			if currentTotal > total and currentTotal < (total + offsetTotal):
				loc = stop['full_location']
				if loc != lastLoc:
					ctx = IrcContext(net, chan, None)
					ctx.reply("Current location: %s" % loc, "@Santa")
					lastLoc = loc
				break;
		return True
		
	@command("track", 0, 0)
	def track(ctx, cmd, arg, *args):
		global chan
		global net
		ctx.reply("Santa tracking comming online... Engaging twitter stream interception engine", "SantaTracker")
		chan = ctx.chan
		net = ctx.irc.network
		updateTimer.start()
		
	@hook("module_unload")
	def timer_stop(ctx):
		updateTimer.stop()
