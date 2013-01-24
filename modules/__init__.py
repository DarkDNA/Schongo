# encoding=utf-8


import sys
import logging
import textwrap
import copy
import time
import threading
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

logger = logging.getLogger("Modules")

logger.setLevel(logging.DEBUG)

MANUAL = "_MANUAL"
AUTO = "_AUTO"

class ModuleInfo:
	name = None
	author = "Unknown"
	version = "Unknown"
	deps = [] # List of type ModuleInfo
	depOf = [] # List of ModuleInfo

	loadType = '_UNK'
	modType = '_NONE'

	def __init__(self, name):
		self.deps = []
		self.depOf = []
		self.cmds = []
		self.name = name

	def __str__(self):
		return "[[ Module %s (Version %s) Written by %s ]]" % (self.name, self.version, self.author)

class IrcContext:
	""" Holds three important context things, and provides some helper methods for quickly replying."""
	irc = None
	chan = None
	who = None
	
	def __init__(self, i, c, w):
		if isinstance(i, str):
			global connections
			# We're being passed a network name, not a actual irc object.
			i = connections[i]

		self.irc = i
		self.chan = c
		self.who = w

		self.isPrivate = (self.chan == self.irc.nick)

		if self.who:
			self.isUs = (self.irc.nick == self.who.nick)
		else:
			self.isUs = False

		fire_hook("context_create", self)

	def reply(self, msg, prefix=None, parse=True, splitnl=True):
		lines = []
		nmsg = [ msg ]
		if '\n' in msg:
			nmsg = msg.split("\n")

		for line in nmsg:
			if prefix is not None:
				line ="[%s] %s" % (prefix, line)
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
		'`O': '\x0F' }

	def say(self, chan, msg, parse=True):
		if parse:
			if msg.startswith("/me "):
				msg = "\x01ACTION %s\x01" % msg[4:]
			for k in self.replacables:
				msg = msg.replace(k, self.replacables[k])
			

		self.irc.say(chan, msg)
		
	def notice(self, msg):
		self.irc.notice(self.who.nick, msg)
	
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
	load_module("_tracking", MANUAL)

	for i in cfg_basic.getlist("autoload modules"):
		load_module(i, MANUAL)
	

def shutdown():
	unloadables = list(mods.keys())
	for i in unloadables:
		unload_module(i)

# Modules

def load_module(mod, loadType, level=logging.WARN):
	if mod in mods:
		logger.info("Module %s already loaded, unloading.", mod);
		unload_module(mod)
	
	# Initiate a ModuleInfo class to store the data of the module

	modInfo = ModuleInfo(mod)
	modInfo.loadType = loadType
	
	# Begin ze actual loadink!
	
	theMod = __import__(mod, globals(), locals(), [], 1)
	modInfo.module = theMod


	if hasattr(theMod, "__info__"):
		# __info__ should contain some additional meta information we may be interested in.

		if "Author" in theMod.__info__:
			modInfo.author = theMod.__info__["Author"]
		else:
			modInfo.author = "Unknown"

		if "Version" in theMod.__info__:
			modInfo.version = theMod.__info__["Version"]
		else:
			modInfo.version = "Unknown"

		modInfo.deps = []
		if "Dependencies" in theMod.__info__:
			logger.info("Dependencies for module %s: %s", mod, theMod.__info__["Dependencies"])
			for m in theMod.__info__["Dependencies"]:
				if m not in mods:
					subModule = load_module(m, AUTO)
				else:
					subModule = mods[m]

				logger.debug("modInfo: %s subModule: %s", modInfo, subModule)

				modInfo.deps += [ subModule ]
				subModule.depOf += [ modInfo ]




	for m in injected_func:
		for cmd in injected_func[m]:
			func = injected_func[m][cmd]
			setattr(theMod, cmd, func)
	
	theMod.logger = logging.getLogger("Module %s" % mod)
	theMod.logger.setLevel(level)

	theMod.cfg = config.get_section("Module/%s" % mod, True)

	theMod.IrcContext = IrcContext

	if mod[0] == "_":
		# This is a special "Utility" module
		# It gets some additional injected data, to better utilise itself
		for m in injected_util_func:
			for cmd in injected_util_func[m]:
				func = injected_util_func[m][cmd]
				setattr(theMod, cmd, func)

		theMod.command = None # Command is illegal inside helper modules
		modInfo.modType = '_UTIL'
	else:
		modInfo.modType = '_NORM'


	# Used to give more decorators for other advanced functionality. :)
	#   Say, @variable
	fire_hook("module_preload", modInfo)
	
	if hasattr(theMod, "onLoad"):
		theMod.onLoad()
		
	mods[mod] = modInfo
	fire_hook("module_load", modInfo);

	return modInfo
	
def unload_module(mod, autoUnloading=False):
	if mod not in mods:
		if "modules.%s" % mod in sys.modules:
			del sys.modules['modules.%s' % mod] # Make sure it's removed from the system modules table.
		return False
	
	# Clean up!

	propName = "modules.%s" % mod
	
	for hook in hooks:
		if propName in hooks[hook]:
			del hooks[hook][propName]

	toDel = []
	
	
	for cmd in commands:
		if commands[cmd].__module__ == propName:
			toDel.append(cmd)
	
	for cmd in toDel:
		del commands[cmd]
	
	if propName in injected_func:
		del injected_func[propName] 
	if propName in injected_util_func:
		del injected_util_func[propName] 
	
	
	modInfo = mods[mod]

	depOn = modInfo.depOf
	for depMod in depOn:
		if depMod.name == mod:
			# I have NO CLUE how this happens, but let's handle it for sanity
			logger.warn("Module is dependency of itself, wtf?")
			continue
		logger.debug("unloading dependent module %s", depMod)
		unload_module(depMod.name, True)


	fire_hook("module_unload", modInfo)

	theMod = modInfo.module

	if hasattr(theMod, "onUnload"):
		theMod.onUnload()

	fire_hook("module_postunload", modInfo)


	# Update and possible remove our dependencies.

	for depMod in modInfo.deps:
		newDeps = []
		for i in depMod.depOf:
			if i.name != mod:
				newDeps += [ i ]
		depMod.depOf = newDeps
		if len(newDeps) == 0 and depMod.loadType == AUTO and not autoUnloading:
			logger.info("Unloading unused module %s", depMod)
			unload_module(depMod.name) # Unload an automatically-loaded module
	

	del mods[mod]
	del sys.modules['modules.%s' % mod]

# Timers


# Decorators

def injected(func):
	if func.__module__ not in injected_func:
		injected_func[func.__module__] = {}

	injected_func[func.__module__][func.__name__] = func
	return func

@injected
def command(name, min=-1, max=-1):
	def retCmd(f):
		if(isinstance(name,list)):
			for n in name:
				commands[n.lower()] = f
		else:
			commands[name.lower()] = f

		f._min = min
		f._max = max
		return f
	return retCmd

@injected
def hook(hook):
	def retHook(f):
		mod = f.__module__

		if hook not in hooks:
			hooks[hook] = {}

		hooks[hook][mod] = f
		return f
	return retHook

@injected
def parent_cmd(name):
	### TODO: Fix this so it assigns the proper __module__ value to the command - atm it will belong to __init__
	@command(name)
	def parentCmd(ctx, cmd, arg):
		if not handle_command(ctx, arg, cmd):
			ctx.error("No such sub-command")

@injected
def privs(level, *groups):
	def func(f):
		f._level = level
		f._groups = groups
		return f
	return func

### Utility injected code

def injected_util(func):
	if func.__module__ not in injected_util_func:
		injected_util_func[func.__module__] = {}

	injected_util_func[func.__module__][func.__name__] = func
	return func

injected_util(injected)
injected_util(fire_hook)

# Core Code

parent_cmd("load")
parent_cmd("unload")

@privs(5, "moduleadmin")
@command(["load module", "load mod"], 1)
def load_cmd(ctx, cmd, arg, *mods):
	"""load module <mod1> [mod2]...
	Loads the given modules"""
	finalOutput = list()
	level = logging.WARN
	for mod in mods:
		if mod in ("-info","-debug","-warn","-normal"):
			# If we are given a special directive (-info or -debug) we will load the remaining mods in
			# The list with a logging output level of the given value.
			if mod == "-info":
				level = logging.INFO
			elif mod == "-debug":
				level = logging.DEBUG
			elif mod == "-normal" or mod == "-warn":
				level = logging.WARN
			continue; # Skip the rest of the processing

		try:
			load_module(mod, MANUAL, level=level)
			finalOutput.append("`B%s`B: loaded" % mod)
		except Exception as e:
			finalOutput.append("`B%s`B: failed (%s)" % (mod,e))
			print_exc()
			unload_module(mod)

	if len(finalOutput) > 0:
		ctx.reply(', '.join(finalOutput), "Load")

@privs(5, "moduleadmin")
@command(["unload mod", "unload module"], 1)
def unload_cmd(ctx, cmd, arg, *mods):
	"""unload module <mod1> [mod2]...
unloads the given modules additional commands may be added to this later, but for now module is the only one"""
	finalOutput = list()
	for mod in mods:
		try:
			unload_module(mod)
			finalOutput.append("`B%s`B: unloaded" % mod)
		except Exception as e:
			finalOutput.append("`B%s`B: failed (%s)" % (mod,e))

	if len(finalOutput) > 0:
		ctx.reply(', '.join(finalOutput), "Unload")

parent_cmd("info")

@command("info permissions", 0, 0)
def info_perms_cmd(ctx, cmd, arg):
	if hasattr(ctx.who, "level"):
		ctx.reply("You are level %d and belong to the following groups: %s" % (
			ctx.who.level,
			", ".join(ctx.who.groups)
			))
	else:
		ctx.reply("There is no permission plugin loaded, please report this to the bot adminenstrator.")


@command(["info module", "info mod"], 1, 1)
def info_mod_cmd(ctx, cmd, arg, m, *args):
	"""info module <module>
Retrieves additional information about the module"""
	ctx.reply("Information available for module %s:" % m)
	try:
		mod = mods[m]

		ctx.reply("Author: %s" % mod.author, m)
		ctx.reply("Version: %s" % mod.version, m)
		if len(mod.deps):
			ctx.reply("Depends on: %s" % ', '.join([ x.name for x in mod.deps ]), m)
		if len(mod.depOf):
			ctx.reply("Depended on by: %s" % ', '.join([ x.name for x in mod.depOf ]), m)

		#ctx.reply("Desc: %s" % mod.desc, m)
	
	except KeyError:
		ctx.reply("[[ Information not available as module is not loaded. ]]")

@command(["info command", "info cmd"])
def info_cmd_cmd(ctx, cmd, arg):
	"""info command <command>
Spits out information for <command> (If we have any)"""
	if arg in commands:
		s = "Command %s" % arg
		theCmd = commands[arg]

		minarg = theCmd._min
		maxarg = theCmd._max

		if minarg != -1 and maxarg == -1:
				s += "(%d+)" % (minarg - 1)
		elif minarg == -1 and maxarg == -1:
			s += "(Any)"
		elif minarg == 0 and maxarg == 0:
			s += "(None)"
		elif minarg == maxarg:
			s += "(%d)" % minarg
		elif minarg != -1 and maxarg != -1:
			s += "(%d to %d)" % (minarg, maxarg)
		else:
			s += ": ** This should never happen **"

		if theCmd.__module__ != "modules":
			s += " from module %s: " % theCmd.__module__.split(".", 1)[1]
		else:
			s += ": "


		parts = (theCmd.__doc__ or "").split("\n", 1)
		usage = parts[0]

		if len(parts) > 1:
			body = parts[1]
		else:
			body = ""

		if usage != "":
			s += usage
		else:
			s += "[[ No usage info given. ]]"

		ctx.reply(s, "Info")

		if body != "":
			ctx.reply(body, "Info")
	else:
		ctx.reply("I don't seem to have any data available for that command.")

@privs(5)
@command("info networks", 0, 0)
def info_networks_cmd(ctx, cmd, arg):
	"""info networks
Spits out information on the networks we are connected to."""
	s = "I am currently connected to the following networks: %s" % ', '.join(list(connections.keys()))
	ctx.reply(s, "Info")

@privs(5)
@command(["info modules","info mods"], 0, 0)
def info_modules_cmd(ctx, cmd, arg):
	"""info modules
Lists the currently loaded modules"""
	s = "I currently have the following modules loaded: %s" % ', '.join(list(mods.keys()))
	ctx.reply(s, "Info")

@privs(5)
@command("info threads", 0, 0)
def info_threads_cmd(ctx, cmd, arg):
	"""info threads
Lists the currently running threads"""
	s = "I currently have the following threads running: %s" 
	s = s % ', '.join([ t.getName() for t in threading.enumerate() ])
	ctx.reply(s, "Info")


@privs(5)
@command("shutdown")
def shutdown_cmd(ctx, cmd, arg):
	"""Shuts down the bot with the given message"""
	shutdown()
	#ctx.irc.disconnect(arg)
	if arg == "":
		arg = "Shutdown ordered by %s" % ctx.who.nick

	for net in connections:
		connections[net].disconnect(arg)
	
def check_command(cmd, lvl, groups):
	if hasattr(cmd, "_level"):
		if cmd._level <= lvl:
			return True
		for g in cmd._groups:
			if g in groups:
				return True
		return False
	return lvl >= 1

def handle_command(ctx, line, parentcmd=None):
	parts = line.split(' ',1)

	if ctx.who is not None:
		if hasattr(ctx.who, "level"):
			wholvl = ctx.who.level
		else:
			wholvl = 1

		if hasattr(ctx.who, "groups"):
			whogroups = ctx.who.groups
		else:
			whogroups = []

	cmd = parts[0]
	if parentcmd is not None:
		cmd = '%s %s' % (parentcmd, cmd)
	if len(parts) > 1:
		arg = parts[1]
		args = arg.split(' ')
	else:
		arg = ""
		args = []
	cmd = cmd.lower()
	if cmd in commands:
		cmdf = commands[cmd];
		# TODO: Implement Max args
		try:
			if not check_command(cmdf, wholvl, whogroups):
				ctx.error("You don't have permission to run that command")
			elif cmdf._min == -1:
				# Dumb command
				cmdf(ctx, cmd, arg);
			elif len(args) < cmdf._min:
				ctx.error("The command %s takes atleast %d arguments, %d given." % (cmd, cmdf._min, len(args)))
			else:
				cmdf(ctx, cmd, arg, *args)
		except Exception as e:
			logger.exception("Error running command %s", cmd)
		return True
	elif parentcmd is None:
		fire_hook("command", ctx, cmd, arg, args)
	else:
		return False
	
@hook("message")
def command_processor(ctx, msg):
	if msg == "":
		return
	if msg[0] == cfg_basic.get("prefix char"):
		handle_command(ctx, msg[1:])
	elif msg.lower().startswith('%s: ' % ctx.irc.nick.lower()):
		handle_command(ctx, msg[len('%s: ' % ctx.irc.nick):]);
		
