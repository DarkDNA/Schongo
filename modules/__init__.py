# encoding=utf-8

from __future__ import with_statement
import sys
import logging
import textwrap
import pickle
import copy
import time
import threading

commands = {}
hooks = {}
filters = {}
mods = {}

cfg_basic = None
config = None

global persist,timers,connections

connections = {}
persist = {}

timers = {}


logger = logging.getLogger("Modules")
logger.setLevel(logging.INFO)

class IrcContext:
	""" Holds three important context things, and provides some helper methods for quickly replying."""
	irc = None
	chan = None
	who = None
	
	def __init__(self, i, c, w):
		if isinstance(i, str):
			# We're being passed a network name, not a actual irc object.
			i = connections[i]

		self.irc = i
		self.chan = c
		self.who = w
	
	def reply(self, msg, prefix=None, parse=True, splitnl=True, splitnliteral=False):
		if '\n' in msg or '\\n' in msg:
			lines = []
			if splitnliteral:
				lines = msg.split('\\n')
			if splitnl:
				if splitnliteral:
					temp = lines
					lines = []
					for line in temp:
						lines.extend(line.split('\n'))
				else:
					lines = msg.split('\n')
			for line in lines:
				if prefix is not None:
					line ="\x02[ %s ]\x02 %s" % (prefix, line)
				if self.chan == self.irc.nick:
					# Private Message
					self.say(self.who.nick, line, parse)
				else:
					self.say(self.chan, line, parse)
		else:
			if prefix is not None:
				msg ="\x02[ %s ]\x02 %s" % (prefix, msg)
			if self.chan == self.irc.nick:
				# Private Message
				self.say(self.who.nick, msg, parse)
			else:
				self.say(self.chan, msg, parse)

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


class TimerThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self, name="Timer Thread")
	
	def run(self):
		global timers
		self.run = True
		while self.run:
			for mod in timers:
				for timer in timers[mod]:
					if timer._curtime == 0:
						try:
							timer(*timer._args, **timer._kwargs)
						except:
							logger.exception("Error while running timer from module %s", timer._mod)

						if timer._repeats:
							timer._curtime = timer._time
						else:
							timer._curtime = -1
					elif timer._curtime > 0:
						timer._curtime -= 1
			time.sleep(1)

	def stop(self):
		self.run = False

timerThread = TimerThread()

# Methods
		
def fire_hook(hook, *args, **kw):
	"""Hooks are fire-and-forget lists for events happening in the bot."""
	if hook in hooks:
		mods = copy.copy(hooks[hook])
		for m in mods:
			try:
				hooks[hook][m](*args, **kw)
			except Exception, e:
				logger.exception("Hook %s crashed when running module %s", hook, m)


def init():
	load_persist()

	for i in cfg_basic.getlist("autoload modules"):
		load_module(i)


	timerThread.start()


def shutdown():
	unloadables = mods.keys()
	for i in unloadables:
		unload_module(i)

	timerThread.stop()

	save_persist()

# Persistance

def load_persist():
	global persist
	try:
		f = file("data/mod_persist.pickle", "rb")
		persist = pickle.load(f)
		f.close()
		logger.info("Persist loaded: %s", persist)
	except:
		logger.warn("Failed to load persist data")
		pass

def save_persist():
	global persist
	logger.info("Saving persist: %s", persist)
	f = file("data/mod_persist.pickle", "wb")
	pickle.dump(persist, f)
	f.flush()
	f.close()
	logger.info("Done.")

# Modules

def load_module(mod):
	if mod in mods:
		logger.warn("Module %s already loaded, unloading.", mod);
		unload_module(mod)
	
	# Begin ze actual loadink!
	
	theMod = __import__(mod, globals(), locals(), [], -1)

	theMod.handle_command = handle_command

	theMod.command = lambda *a, **kw : command_mod(mod, *a, **kw)
	theMod.hook = lambda h : hook_mod(mod, h)
	theMod.timer = lambda *a, **kw : timer_mod(mod, *a, **kw)
	theMod.parent_cmd = lambda n : parent_cmd_mod(mod, n)

	theMod.logger = logging.getLogger("Module %s" % mod)
	theMod.cfg = config.get_section("Module/%s" % mod, True)

	theMod.IrcContext = IrcContext

	if hasattr(theMod, "__persist__"):
		global persist
		if mod in persist:
			for i in theMod.__persist__:
				if i in persist[mod]:
					setattr(theMod, i, persist[mod][i]) # This could certanly be cleaner.

	# Used to give more decorators for other advanced functionality. :)
	#   Say, @variable
	fire_hook("module_preload", mod, theMod)
	
	if hasattr(theMod, "onLoad"):
		theMod.onLoad()
		
	mods[mod] = theMod
	fire_hook("module_load", mod, theMod);
	
def unload_module(mod):
	if mod not in mods:
		return False
	
	# Clean up!
	
	for hook in hooks:
		if mod in hook:
			del hook[mod]

	global timers
	if mod in timers:
		del timers[mod]
	
	toDel = []
	
	for cmd in commands:
		if commands[cmd]._mod == mod:
			toDel.append(cmd)
	
	for cmd in toDel:
		del commands[cmd]
	
	fire_hook("module_unload", mod)
	
	theMod = mods[mod]

	if hasattr(theMod, "onUnload"):
		theMod.onUnload()


	try:
		if hasattr(theMod, "__persist__"):
			global persist
			persist[mod] = {}
			for i in theMod.__persist__:
				persist[mod][i] = getattr(theMod, i)

	except AttributeError, e:
		logger.warn("Error persisting data for module %s: %s", mod, e)
		pass
	
	del mods[mod]
	del sys.modules['modules.%s' % mod]

# Timers

def timer_start(mod, timer, args, kwargs):
	timer._args = args
	timer._kwargs = kwargs
	timer._curtime = timer._time

def timer_cancel(mod, timer):
	timer._curtime = -1

# Decorators

def command_mod(mod, name, min=-1, max=-1):
	def retCmd(f):
		if(isinstance(name,list)):
			for n in name:
				commands[n] = f
		else:
			commands[name] = f
		f._mod = mod
		f._min = min
		f._max = max		
		return f
	return retCmd

def hook_mod(mod, hook):
	def retHook(f):
		if hook not in hooks:
			hooks[hook] = {}
		hooks[hook][mod] = f
		return f
	return retHook

def timer_mod(mod, time, repeats=False):
	def retTimer(f):
		global timers
		if mod not in timers:
			timers[mod] = []

		timers[mod].append(f)

		f._time = time
		f._repeats = repeats
		f._curtime = -1 

		f.start = lambda *a, **kw : timer_start(mod, f, a, kw)
		f.cancel = lambda : timer_cancel(mod, f)
		return f
	return retTimer


def parent_cmd_mod(mod, name):
	@command_mod(mod, name)
	def parentCmd(ctx, cmd, arg):
		if not handle_command(ctx, arg, cmd):
			ctx.error("No such sub-command")

# Helpers

command = lambda *a, **kw : command_mod("__init__", *a, **kw)
hook = lambda h : hook_mod("__init__", h)
parent_cmd = lambda n : parent_cmd_mod("__init__", n)

# Core Code

parent_cmd("load")
parent_cmd("unload")

@command(["load module", "load mod"], 1)
def load_cmd(ctx, cmd, arg, *args):
	"""load module <mod1> [mod2]...
	Loads the given modules"""
	modulesLoaded = 0
	for mod in args:
		try:
			load_module(mod)
			ctx.reply("Done.", "Load")
			modulesLoaded += 1
		except Exception, e:
			ctx.reply("Error loading %s: %s" % (mod,e), "Load")
	if modulesLoaded > 0:
		if modulesLoaded == 1:
			ctx.reply("Loaded %s module" % modulesLoaded, "Load")
		else:
			ctx.reply("Loaded %s modules" % modulesLoaded, "Load")

@command(["unload mod", "unload module"], 1)
def unload_cmd(ctx, cmd, arg, *mods):
	"""unload module <mod1> [mod2]...
unloads the given modules additional commands may be added to this later, but for now module is the only one"""
	modulesUnloaded = 0
	for mod in args:
		try:
			unload_module(mod)
			ctx.reply("Done.", "Unload")
			modulesUnloaded += 1
		except Exception, e:
			ctx.reply("Error unloading %s: %s" % (mod,e), "Unload")

	if modulesUnloaded > 0:
		if modulesUnloaded == 1:
			ctx.reply("Unloaded %s module" % modulesUnloaded, "Unload")
		else:
			ctx.reply("Unloaded %s modules" % modulesUnloaded, "Unload")

parent_cmd("info")

@command(["info module", "info mod"], 1, 1)
def info_mod_cmd(ctx, cmd, arg, mod, *args):
	"""info module <module>
Retrieves additional information about the module"""
	ctx.reply("Information available for module %s:" % args[0])
	try:
		m = args[0]
		mod = mods[m]
		if hasattr(mod, "__doc__"):
			doc = mod.__doc__.split("\n")
			if doc[0] == "":
				doc = doc[1]
			else:
				doc = doc[0]
		else:
			doc = "*** This module doesn't provide a doc string, yell at the author."

		ctx.reply("%s" % doc, m, False)
		try:
			info = mod.__info__
			ctx.reply("Author: %s" % info['Author'], m, False)
			ctx.reply("Version: %s" % info['Version'], m, False)
		except AttributeError:
			ctx.reply("Additional information not available")
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
				s += "(>%d)" % (minarg - 1)
		elif minarg == -1 and maxarg == -1:
			s += "(Any)"
		elif minarg == maxarg:
			s += "(%d)" % minarg
		elif minarg != -1 and maxarg != -1:
			s += "(%d to %d)" % (minarg, maxarg)
		else:
			s += ": ** This should never happen **"

		if theCmd._mod != "__init__":
			s += " from module %s: " % theCmd._mod
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

@command("info networks", 0, 0)
def info_networks_cmd(ctx, cmd, arg):
	"""info networks
Spits out information on the networks we are connected to."""
	s = "I am currently connected to the following networks: %s" % ', '.join(connections.keys())
	ctx.reply(s, "Info")

@command("shutdown")
def shutdown_cmd(ctx, cmd, arg):
	"""Shuts down the bot with the given message"""
	shutdown()
	#ctx.irc.disconnect(arg)
	if arg == "":
		arg = "Shutdown ordered by %s" % ctx.who.nick

	for net in connections:
		connections[net].disconnect(arg)
	
def handle_command(ctx, line, parentcmd=None):
	parts = line.split(' ',1)
	cmd = parts[0]
	if parentcmd is not None:
		cmd = '%s %s' % (parentcmd, cmd)
	if len(parts) > 1:
		arg = parts[1]
		args = arg.split(' ')
	else:
		arg = ""
		args = []
	if cmd in commands:
		cmdf = commands[cmd];
		# TODO: Implement Max args
		try:
			if cmdf._min == -1:
				# Dumb command
				cmdf(ctx, cmd, arg);
			elif len(args) < cmdf._min:
				ctx.error("The command %s takes atleast %d arguments, %d given." % (cmd, cmdf._min, len(args)))
			else:
				cmdf(ctx, cmd, arg, *args)
		except Exception, e:
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
	elif msg.startswith('%s: ' % ctx.irc.nick):
		handle_command(ctx, msg[len('%s: ' % ctx.irc.nick):]);
		
