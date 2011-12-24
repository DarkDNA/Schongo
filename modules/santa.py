#!/usr/bin/python3
# coding=utf-8

"""
The Santa tracking module for schongo :D
"""

import urllib.request as request
from time import time
import json
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1",
	"Dependencies": [
		"_timer"
	]
}
global chan, net, lastLoc
chan = ''
net = ''
dataURL = "http://www.noradsanta.org/js/data.js"
lastLoc = ''
def onLoad():
	data = request.urlopen(request.Request(dataURL)).read()
	data = data.split(b"=",1)[1]
	locList = json.loads(data.decode('utf-8'))
	print("Entries: %d" % len(locList))

	@timer(60,True)
	def updateTimer():
		global lastLoc,net,chan
		currentTotal = (int(time()) - 1324710000) / 60;

		for stop in locList:
			t = stop['time'].split(':')
			h = int(t[0])
			m = int(t[1])
			total = (h * 60) + m
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
		ctx.reply("Santa tracking comming online... Engaging json intercept-omatic", "SantaTracker")
		chan = ctx.chan
		net = ctx.irc.network
		updateTimer.start()
	@hook("module_unload")
	def timer_stop(ctx):
		updateTimer.stop()
