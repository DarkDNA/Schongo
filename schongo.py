#!/usr/bin/env python3
# encoding=utf-8
from __future__ import with_statement

import getopt
import logging
import logging.config
import os.path
import sys

from schongo import module_loader, tracking, timers, commands, persistance

from schongo.config import Config
from schongo.irc import IrcClient

global connections

connections = 0

version = "0.1a"

if os.path.isdir(".git"):
    # We're running from a git tree, let's pull the revision number, shall we?
    with open(".git/HEAD") as f:
        ref = f.read().strip()
        ref = ref.split(': ', 1)[1]
        with open(".git/%s" % ref) as f2:
            version = f2.read()[:8]


class SchongoClient(IrcClient):
    def __init__(self, network, cfg):

        server = cfg.get("server")
        port = cfg.getint("port")
        nicks = cfg.getlist("nicks")
        ident = cfg.get("ident")
        realname = cfg.get("real name")

        def get(opt):
            try:
                return cfg.get(opt)
            except:
                return None

        self.user_modes = get("user modes")

        self._ns_name = get("nickserv name")
        self._ns_pass = get("nickserv password")
        self._ns_find = get("nickserv find")

        if self._ns_find is None:
            self._ns_find = "is registered"

        if self._ns_name is None:
            self._ns_name = "NickServ"

        if self._ns_pass is None:
            self._ns_authed = True
        else:
            self._ns_authed = False

        channels = cfg.getlist("channels")

        IrcClient.__init__(self, server, port, nicks, ident, realname)

        if channels is None:
            channels = ["#lobby"]

        self.channels = channels

        if network is not None:
            self.network = network
        else:
            self.network = server

        self.logger = logging.getLogger("IrcSocket(%s)" % self.network)

        global connections
        connections += 1

    # Overrides Thread
    def getName(self):
        return "IrcSocket(%s)" % self.network

    # Overrides IrcClient, and calls super
    def onConnected(self):
        IrcClient.onConnected(self)

        if self.user_modes is not None:
            self.sendMessage("MODE", self.nick, self.user_modes)

        module_loader.fire_hook("irc_connected", self)
        for i in self.channels:
            self.join_channel(i)

    # Overrides IrcClient, and calls super
    def onDisconnected(self):
        module_loader.fire_hook("irc_disconnected", self)
        IrcClient.onDisconnected(self)
        global connections

        connections -= 1

        if connections == 0:
            self.logger.info("Shutting down.")
            module_loader.shutdown()

    # Overrides IrcClient
    def onMsg(self, chan, who, what):
        module_loader.fire_hook("irc_message", module_loader.IrcContext(self, chan, who), what)

    # Overrides IrcClient
    def onAction(self, chan, who, what):
        module_loader.fire_hook("irc_action", module_loader.IrcContext(self, chan, who), what)

    # Overrides IrcClient
    def onCtcp(self, chan, who, cmd, arg):
        if cmd == "VERSION":
            self.notice(who.nick, "\x01VERSION Schongo Bot %s\x01" % version)
        elif cmd == "PING":
            self.notice(who.nick, "\x01PING %s\x01" % arg)
        else:
            module_loader.fire_hook("irc_ctcp", module_loader.IrcContext(self, chan, who), cmd, arg)

    # Overrides IrcClient
    def onJoin(self, who, chan):
        module_loader.fire_hook("irc_join", module_loader.IrcContext(self, chan, who))

    # Overrides IrcClient
    def onPart(self, who, chan, msg):
        module_loader.fire_hook("irc_part", module_loader.IrcContext(self, chan, who))

    # Overrides IrcClient
    def onQuit(self, who, message):
        module_loader.fire_hook("irc_quit", module_loader.IrcContext(self, None, who))

    # Overrides IrcClient
    def onTopic(self, who, chan, topic):
        module_loader.fire_hook("irc_topic", module_loader.IrcContext(self, chan, who), topic)

    # Overrides IrcClient
    def onNick(self, old, new):
        module_loader.fire_hook("irc_nick", module_loader.IrcContext(self, None, old), new)

    # Overrides IrcClient
    def onMode(self, who, chan, mode, args):
        module_loader.fire_hook("irc_mode", module_loader.IrcContext(self, chan, who), mode, args)

    def onNotice(self, target, who, message):
        if not self._ns_authed and who.nick == self._ns_name:
            if self._ns_find in message:
                self.say(self._ns_name, "IDENTIFY %s" % self._ns_pass)
        else:  # Intentionally don't allow it to intercept NickServ messages.
            module_loader.fire_hook("irc_notice", module_loader.IrcContext(self, target, who), message);

    # Overrides IrcClient
    def onMessage(self, msg):
        # Call the parent so we still function.
        IrcClient.onMessage(self, msg)
        # Fire off an event for module_loader to eat
        module_loader.fire_hook("irc_%s" % msg.command,
                                module_loader.IrcContext(self, None, msg.origin),
                                msg)


def main(argv):
    opts, args = getopt.getopt(argv, "v:c", ["debug", "config="])
    print(opts)

    debug = False
    configFile = None

    dn = os.path.dirname(__file__)
    if dn is not "":
        os.chdir(dn)
    del dn

    for arg, val in opts:
        if arg == "--debug" or arg == "-v":
            debug = True
        elif arg == "--config" or arg == "-c":
            configFile = val

    if configFile is None:
        configFile = "data/config-debug.cfg" if debug else "data/config.cfg"

    if not os.path.isfile(configFile):
        if os.path.isfile("data/config.cfg"):
            logging.warn("Config file %s missing, reverting to default" % configFile)
            configFile = "data/config.cfg"
        else:
            logging.error("""We are missing a config file, please look at the example.cfg for help on making a new config, and name it config.cfg or pass a config file using --config

The config file should go in the data directory""")
            return

    #logging.basicConfig(level=(logging.DEBUG if debug else logging.WARN))
    logging.config.fileConfig("data/logging.cfg")



    config = Config();

    logging.info("Reading config file: %s" % configFile)
    try:
        config.read(configFile)
    except Exception as e:
        logging.error("Error reading config file: %s" % e)
        return

    if debug:
        logging.info("Debug mode activated")

    basic = config.get_section("Basic")

    module_loader.cfg_basic = basic
    module_loader.config = config
    module_loader.init()

    tracking.init()

    timers.init()

    commands.cfg_basic = basic
    commands.init()

    persistance.init()

    schongos = {}

    for i in basic.getlist("networks"):
        net = config.get_section("Network/%s" % i)

        sch = SchongoClient(i, net)
        sch.connect()
        sch.start()

        schongos[i] = sch

    commands.connections = schongos

    return schongos


if __name__ == "__main__":
    main(sys.argv[1:])
