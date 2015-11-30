# encoding=utf-8

import sys
import logging
import copy
import threading
import importlib
import os
import os.path

from traceback import print_exc

commands = {}
hooks = {}
filters = {}
mods = {}

cfg_basic = None
config = None

global connections
connections = {}

injected_func = {}
injected_util_func = {}

logger = logging.getLogger("module_loader")
logger.setLevel(logging.DEBUG)

MANUAL = "_MANUAL"
AUTO = "_AUTO"

class ModuleInfo:
    def __init__(self, name):
        self.module = None

        self.name = name
        self.author = "Unknown"
        self.version = "Unknown"

        self.deps = []  # List of ModuleInfo
        self.depOf = []  # List of ModuleInfo

        self.loadType = '_UNK'
        self.modType = '_NONE'

        self.deps = []
        self.depOf = []

    def __str__(self):
        return "[[ Module %s (Version %s) Written by %s ]]" % (self.name, self.version, self.author)


class IrcUser:
    def __init__(self, who):
        if who is not None:
            self.nick = who.nick
            self.ident = who.ident
            self.host = who.host
        else:
            self.nick = None
            self.ident = None
            self.host = None

        # Security stuff.
        self.level = 0
        self.groups = []

class IrcContext:
    """ Holds three important context things, and provides some helper methods for quickly replying."""

    def __init__(self, i, c, w):
        if isinstance(i, str):
            global connections
            # We're being passed a network name, not a actual irc object.
            i = connections[i]

        self.irc = i
        self.chan = c
        self.who = IrcUser(w)

        self.isPrivate = (self.chan == self.irc.nick)

        if self.who:
            self.isUs = (self.irc.nick == self.who.nick)
        else:
            self.isUs = False

        fire_hook("context_create", self)

    def reply(self, msg, prefix=None, parse=True, splitnl=True):
        lines = []
        nmsg = [msg]
        if '\n' in msg:
            nmsg = msg.split("\n")

        for line in nmsg:
            if prefix is not None:
                line = "[%s] %s" % (prefix, line)
            if self.chan == self.irc.nick:
                # Private Message
                self.say(self.who.nick, line, parse)
            else:
                self.say(self.chan, line, parse)

    def error(self, msg):
        self.reply(msg, "Error")

    replacables = {
        '`B': '\x02',
        '`U': '\x1F',
        '`O': '\x0F'}

    def say(self, chan, msg, parse=True):
        if parse:
            if msg.startswith("/me "):
                msg = "\x01ACTION %s\x01" % msg[4:]
            for k in self.replacables:
                msg = msg.replace(k, self.replacables[k])

        self.irc.say(chan, msg)

    def notice(self, who, msg, prefix=None, parse=False):
        if parse:
            for k in self.replacables:
                msg = msg.replace(k, self.replacables[k])

        lines = []
        nmsg = [msg]
        if '\n' in msg:
            nmsg = msg.split("\n")

        for line in nmsg:
            if prefix is not None:
                line = "[%s] %s" % (prefix, line)

            self.irc.notice(who, line)

    def ctcp_reply(self, cmd, arg):
        self.notice("\x01%s %s\x01" % (cmd, arg))

    @staticmethod
    def fromString(string, ctx=None):
        parts = string.split("->")

        if len(parts) > 2:
            net = parts[0]
            chan = parts[1]
        elif ctx is not None:
            net = ctx.irc
            chan = string
        else:
            return None

        return IrcContext(net, chan, None)


# Methods

def fire_hook(hook, *args, **kw):
    """Hooks are fire-and-forget lists for events happening in the bot."""
    if hook in hooks:
        mods = copy.copy(hooks[hook])
        for m in mods:
            try:
                hooks[hook][m](*args, **kw)
            except Exception as e:
                logger.exception("Hook %s crashed when running module %s", hook, m)


def init():
    logger.info("Initalising module system.")

    for i in cfg_basic.getlist("autoload modules"):
        load_module(i, MANUAL)


def shutdown():
    unloadables = list(mods.keys())
    for i in unloadables:
        unload_module(i)


# Modules

def load_module(name, loadType, level=logging.WARN):
    if name in mods:
        logger.info("Module %s already loaded, unloading.", name);
        unload_module(name)

    # Initiate a ModuleInfo class to store the data of the module

    moduleInfo = ModuleInfo(name)
    moduleInfo.loadType = loadType

    # Begin ze actual loadink!
    module = None

    modZip = os.path.abspath("./data/modules/" + name + ".zip")

    if os.path.exists(modZip):
        bkup = sys.path
        sys.path = [modZip] + sys.path

        importlib.invalidate_caches()
        module = __import__(name, globals(), locals(), ["onLoad", "__info__"], 0)
        sys.path = bkup
    else:
        module = __import__("modules." + name, globals(), locals(), ["onLoad", "__info__"], 0)

    moduleInfo.module = module

    if hasattr(module, "__info__"):
        # __info__ should contain some additional meta information we may be interested in.

        if "Author" in module.__info__:
            moduleInfo.author = module.__info__["Author"]
        else:
            moduleInfo.author = "Unknown"

        if "Version" in module.__info__:
            moduleInfo.version = module.__info__["Version"]
        else:
            moduleInfo.version = "Unknown"

        moduleInfo.deps = []
        if "Dependencies" in module.__info__:
            logger.info("Dependencies for module %s: %s", name, module.__info__["Dependencies"])
            for m in module.__info__["Dependencies"]:
                if m not in mods:
                    subModule = load_module(m, AUTO)
                else:
                    subModule = mods[m]

                logger.debug("moduleInfo: %s subModule: %s", moduleInfo, subModule)

                moduleInfo.deps += [subModule]
                subModule.depOf += [moduleInfo]

    # for m in injected_func:
    #     for cmd in injected_func[m]:
    #         func = injected_func[m][cmd]
    #         setattr(module, cmd, func)

    module.logger = logging.getLogger("Module %s" % name)
    module.logger.setLevel(level)

    module.cfg = config.get_section("Module/%s" % name, True)

    module.IrcContext = IrcContext

    if name[0] == "_":
        # This is a special "Utility" module
        # It gets some additional injected data, to better utilise itself
        for m in injected_util_func:
            for cmd in injected_util_func[m]:
                func = injected_util_func[m][cmd]
                setattr(module, cmd, func)

        module.command = None  # Command is illegal inside helper modules
        moduleInfo.modType = '_UTIL'
    else:
        moduleInfo.modType = '_NORM'

    # Used to give more decorators for other advanced functionality. :)
    #   Say, @variable
    fire_hook("module_preload", moduleInfo)

    if hasattr(module, "onLoad"):
        module.onLoad()

    mods[name] = moduleInfo
    fire_hook("module_load", moduleInfo);

    return moduleInfo


def unload_module(name, autoUnloading=False):
    propName = "modules.%s" % name

    if name not in mods:
        if "modules.%s" % name in sys.modules:
            del sys.modules['modules.%s' % name]  # Make sure it's removed from the system modules table.
        return False

    if name in sys.modules:
        propName = name

    # Clean up!

    for hook in hooks:
        if propName in hooks[hook]:
            del hooks[hook][propName]

    if propName in injected_func:
        del injected_func[propName]

    if propName in injected_util_func:
        del injected_util_func[propName]

    moduleInfo = mods[name]

    depOn = moduleInfo.depOf
    for depMod in depOn:
        if depMod.name == name:
            # I have NO CLUE how this happens, but let's handle it for sanity
            logger.warn("Module is dependency of itself, wtf?")
            continue
        logger.debug("unloading dependent module %s", depMod)
        unload_module(depMod.name, True)

    fire_hook("module_unload", moduleInfo)

    theMod = moduleInfo.module

    if hasattr(theMod, "onUnload"):
        theMod.onUnload()

    fire_hook("module_postunload", moduleInfo)

    # Update and possible remove our dependencies.

    for depMod in moduleInfo.deps:
        newDeps = []
        for i in depMod.depOf:
            if i.name != name:
                newDeps += [i]
        depMod.depOf = newDeps
        if len(newDeps) == 0 and depMod.loadType == AUTO and not autoUnloading:
            logger.info("Unloading unused module %s", depMod)
            unload_module(depMod.name)  # Unload an automatically-loaded module

    del mods[name]
    del sys.modules[propName]

# Decorators

def injected(func):
    logger.info("@injected is deprecated, please don't use it.")

    if func.__module__ not in injected_func:
        injected_func[func.__module__] = {}

    injected_func[func.__module__][func.__name__] = func
    return func

def hook(hook):
    def retHook(f):
        mod = f.__module__

        if hook not in hooks:
            hooks[hook] = {}

        hooks[hook][mod] = f
        return f

    return retHook

### Utility injected code

def injected_util(func):
    if func.__module__ not in injected_util_func:
        injected_util_func[func.__module__] = {}

    injected_util_func[func.__module__][func.__name__] = func
    return func


injected_util(injected)
injected_util(fire_hook)