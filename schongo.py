#!/usr/bin/env python
# encoding=utf-8
from irc import IrcClient
import logging
import logging.config
import json
import modules
import sys
import getopt
import os.path

from config import Config


version = "0.1a"

class SchongoClient(IrcClient):
	def __init__(self, server, port=6667, nicks=None, ident=None, realname=None, network=None, channels=None):
		IrcClient.__init__(self, server, port, nicks, ident, realname)

		if channels is None:
			channels = ["#lobby"]

		self.channels = channels


		if network is not None:
			self.network = network
		else:
			self.network = server
		
		self.logger = logging.getLogger("IrcSocket(%s)" % self.network)

	# Overrides Thread
	def getName(self):
		return "IrcSocket(%s)" % self.network


	# Overrides IrcClient, and calls super	
	def onConnected(self):
		IrcClient.onConnected(self)
		modules.fire_hook("connected", self)
		for i in self.channels:
			self.join_channel(i)	

	# Overrides IrcClient, and calls super
	def onDisconnected(self):
		modules.fire_hook("disconnected", self)
		IrcClient.onDisconnected(self)
	
	# Overrides IrcClient
	def onMsg(self, chan, who, what):
		modules.fire_hook("message", modules.IrcContext(self, chan, who), what)
	
	# Overrides IrcClient
	def onAction(self, chan, who, what):
		modules.fire_hook("action", modules.IrcContext(self, chan, who), what)
	
	# Overrides IrcClient
	def onCtcp(self, chan, who, cmd, arg):
		if cmd == "VERSION":
			self.notice(who.nick, "\x01VERSION Schongo Bot %s\x01" % version)
		else:
			modules.fire_hook("ctcp", modules.IrcContext(self, chan, who), what)

def main(argv):
	opts, args = getopt.getopt(argv, "v:c", [ "debug", "config=" ])
	print(opts)

	debug = False
	configFile = None

	for arg,val in opts:
		if arg == "--debug" or arg == "-v":
			debug = True
		elif arg == "--config" or arg == "-c":
			configFile = val

	if configFile is None:
		configFile = debug and "data/config-debug.cfg" or "data/config.cfg"

	if not os.path.isfile(configFile):
		if os.path.isfile("data/config.cfg"):
			logging.warn("Config file %s missing, reverting to default" % configFile)
			configFile = "data/config.cfg"
		else:
			logging.error("""We are missing a config file, please look at the example.cfg for help on making a new config, and name it config.cfg or pass a config file using --config

The config file should go in the data directory""")
			return
	

	logging.basicConfig(level=(debug and logging.DEBUG or logging.WARN))
	#logging.config.fileConfig("logging.cfg")



	config = Config();

	logging.info("Reading config file: %s" % configFile)
	try:
		config.read(configFile)
	except Exception,e:
		logging.error("Error reading config file: %s" % e)
		return

	if debug:
		logging.info("Debug mode activated")

	basic = config.get_section("Basic")

	modules.cfg_basic = basic
	modules.config = config

	modules.init()

	schongos = {}

	for i in basic.getlist("networks"):
		net = config.get_section("Network/%s" % i)
		sch = SchongoClient(
			server=net.get("server"),
			port=net.getint("port"),
			nicks=net.getlist("nicks"),
			ident=net.get("ident"),
			realname=net.get("real name"),
			network=i,
			channels=net.getlist("channels")
		)
		sch.connect()
		sch.start()
		schongos[i] = sch
	
	modules.connections = schongos

	return schongos


if __name__ == "__main__":
	main(sys.argv[1:])
