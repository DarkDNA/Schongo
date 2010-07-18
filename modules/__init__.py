import sys
import logging
import textwrap

commands = {}
hooks = {}
filters = {}
mods = {}

cfg_basic = None
config = None

connections = {}

logger = logging.getLogger("Modules")

class IrcContext:
	""" Holds three important context things, and provides some helper methods for quickly replying."""
	irc = None
	chan = None
	who = None
	
	def __init__(self, i, c, w):
		self.irc = i
		self.chan = c
		self.who = w
	
	def reply(self, msg, prefix=None, parse=True):
		if prefix is not None:
			msg = "\x02[ %s ]\x02 %s" % (prefix, msg)

		if self.chan == self.irc.nick:
			# Private Message
			self.say(self.who.nick, msg, parse)
		else:
			self.say(self.chan, msg, parse)

	def error(self, msg):
		self.reply(msg, "Error")


	def say(self, chan, msg, parse=True):
		if parse:
			if msg.startswith("/me "):
				msg = "\x01ACTION %s\x01" % msg[4:]

		self.irc.say(chan, msg)
		
	def notice(self, msg):
		self.irc.notice(self.who.nick, msg)
	
	def ctcp_reply(self, cmd, arg):
		self.notice("\x01%s %s\x01" % (cmd, arg))

# Methods
		
def fire_hook(hook, *args, **kw):
	"""Hooks are fire-and-forget lists for events happening in the bot."""
	if hook in hooks:
		for m in hooks[hook]:
			try:
				hooks[hook][m](*args, **kw)
			except Exception, e:
				logger.warn("Hook %s crashed when running module %s: %s", hook, m, e)


def init():
	for i in cfg_basic.getlist("autoload modules"):
		load_module(i)

def load_module(mod):
	if mod in mods:
		logger.warn("Module %s already loaded, unloading.", mod);
		unload_module(mod)
	
	# Begin ze actual loadink!
	
	theMod = __import__(mod, globals(), locals(), [], -1)

	theMod.command = lambda *a, **kw : command_mod(mod, *a, **kw)
	theMod.hook = lambda h : hook_mod(mod, h)

	theMod.logger = logging.getLogger("Module %s" % mod)
	theMod.config = config.get_section("Module/%s" % mod, True)
	
	# Used to give more decorators for other advanced functionality. :)
	#   Say, @variable
	fire_hook("module_preload", mod, theMod)
	
	try:
		theMod.onLoad()
	except AttributeError:
		pass
	
	mods[mod] = theMod
	fire_hook("module_load", mod, theMod);
	
def unload_module(mod):
	if mod not in mods:
		return False
	
	# Clean up!
	
	for hook in hooks:
		if mod in hook:
			del hook[mod]
	
	toDel = []
	
	for cmd in commands:
		if commands[cmd]._mod == mod:
			#del commands[cmd];
			toDel.append(cmd)
	
	for cmd in toDel:
		del commands[cmd]
	
	fire_hook("module_unload", mod)
	
	try:
		mods[mod].onUnload()
	except AttributeError:
		pass
	
	del mods[mod]
	del sys.modules['modules.%s' % mod]

# Decorators
global command, hook;

def command_mod(mod, name, min=-1, max=-1):
	def retCmd(f):
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


command = lambda *a, **kw : command_mod("__init__", *a, **kw)
hook = lambda h : hook_mod("__init__", h)
	
# Core Code
	
@command("load", 2)
def load_cmd(ctx, cmd, arg, what, *args):
	"""load module <mod1> [mod2]..."""
	if what == "module" or what == "mod":
		for mod in args:
			try:
				load_module(mod)
			except Exception, e:
				ctx.reply("Error loading %s: %s" % (mod,e), "Load")
		ctx.reply("Done.", "Load")
	else:
		ctx.error("Unknown 'load' sub-command: %s" % what);

@command("unload", 2)
def unload_cmd(ctx, cmd, arg, what, *args):
	"""unload module <mod1> [mod2]..."""
	if what == "module" or what == "mod":
		for mod in args:
			try:
				unload_module(mod)
			except Exception, e:
				ctx.reply("Error unloading %s: %s" % (mod,e), "Unload")
		ctx.reply("Done.", "Unload")
	else:
		ctx.error("Unknown 'unload' sub-command: %s" % what);

@command("info", 2, 2)
def info_cmd(ctx, cmd, arg, what, *args):
	"""info <module|command> <data>"""
	if what == "module" or what == "mod":
		ctx.reply("Information available for module %s:" % args[0])
		try:
			mod = mods[args[0]]
			doc = (dbgmod.__doc__ or "").split("\n", 1)[0];
			if doc == "":
				doc = "*** This module doesn't provide a doc string, yell at the author."
			ctx.reply("%s" % doc, mod, False)
			try:
				info = mod.__info__
				ctx.reply("Author: %s" % info['Author'], mod, False)
				ctx.reply("Version: %s" % info['Version'], mod, False)
			except AttributeError:
				ctx.reply("Additional information not available")
		except KeyError:
			ctx.reply("[[ Information not available as module is not loaded. ]]")
	elif what == "command" or what == "cmd":
		c = args[0]
		if c in commands:
			#ctx.reply("Info for command %s" % c)
			#ctx.reply("[%s] %d min args" % (c, c._args))
			s = "Command %s" % c
			minarg = commands[c]._min
			maxarg = commands[c]._max
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
			if commands[c]._mod != "__init__":
				s += " from module %s: " % commands[c]._mod
			else:
				s += ": "


			parts = (commands[c].__doc__ or "").split("\n", 1)
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
	else:
		ctx.error("Unknown info element: %s" % what)

@command("shutdown")
def shutdown_cmd(ctx, cmd, arg):
	ctx.irc.disconnect(arg)
	


def handle_command(ctx, line):
	parts = line.split(' ',1)
	cmd = parts[0]
	if len(parts) > 1:
		arg = parts[1]
		args = arg.split(' ')
	else:
		arg = ""
		args = []
	if cmd in commands:
		cmdf = commands[cmd];
		# TODO: Implement Max args
		if cmdf._min == -1:
			# Dumb command
			cmdf(ctx, cmd, arg);
		elif len(args) < cmdf._min:
			ctx.error("The command %s takes atleast %d arguments, %d given." % (cmd, cmdf._min, len(args)))
		else:
			commands[cmd](ctx, cmd, arg, *args)
	else:
		fire_hook("command", ctx, cmd, arg, args)
	
@hook("message")
def command_processor(ctx, msg):
	if msg[0] == cfg_basic.get("prefix char"):
		handle_command(ctx, msg[1:])
	elif msg.startswith('%s: ' % ctx.irc.nick):
		handle_command(ctx, msg[len('%s: ' % ctx.irc.nick):]);
		
