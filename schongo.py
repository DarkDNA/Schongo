#!/usr/bin/env python
from irc import IrcClient
import logging
import json
import modules
import sys
import getopt

version = "0.1a"

class SchongoClient(IrcClient):
	def __init__(self):
		IrcClient.__init__(self,
			server="irc.darkdna.net",
			port=6667,
			nicks=["Schongo", "Schongo1"],
			ident="schongo",
			realname="Schongo"
		)
	
	def onConnected(self):
		IrcClient.onConnected(self)
		modules.fire_hook("connected", self)
		self.join_channel("#lobby")
	
	def onDisconnected(self):
		modules.fire_hook("disconnected", self)
		IrcClient.onDisconnected(self)
	
	def onMsg(self, chan, who, what):
		modules.fire_hook("message", modules.IrcContext(self, chan, who), what)
	
	def onAction(self, chan, who, what):
		modules.fire_hook("action", modules.IrcContext(self, chan, who), what)
	
	def onCtcp(self, chan, who, cmd, arg):
		if cmd == "VERSION":
			self.notice(who.nick, "\x01VERSION Schongo Bot %s\x01" % version)
		else:
			modules.fire_hook("ctcp", modules.IrcContext(self, chan, who), what)

def main(argv):
	opts, args = getopt.getopt(argv, "v:c", [ "debug", "config=" ])
	print(opts)

	debug = False

	for arg,val in opts:
		if arg == "--debug" or arg == "v":
			debug = True
	logging.basicConfig(level=(debug and logging.DEBUG or logging.WARN))
	if debug:
		logging.info("Debug mode activated")

	conn = SchongoClient();
	conn.connect()

	conn.start()
	return conn
	
if __name__ == "__main__":
	main(sys.argv[1:])
