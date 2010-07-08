import sys
import logging

commands = {}
hooks = {}
mods = {}

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
	
	def reply(self, msg):
		if self.chan == self.irc.nick:
			# Private Message
			self.irc.say(self.who.nick, msg)
		else:
			self.irc.say(self.chan, msg)
		
	def notice(self, msg):
		self.irc.notice(self.who.nick, msg)
	
	def ctcp_reply(self, cmd, arg):
		self.notice("\x01%s %s\x01" % (cmd, arg))

# Commands
		
def fire_hook(hook, *args, **kw):
	if hook in hooks:
		for m in hooks[hook]:
			try:
				hooks[hook][m](*args, **kw)
			except Exception, e:
				logger.warn("Hook {hook} crashed for module {module}: {exc}".format(hook=hook, module=m, exc=e))
	
def load_module(mod):
	if mod in mods:
		#print("@@@ Module `%s' already loaded" % mod)
		logger.warn("Module {mod} already loaded, unloading.".format(mod=mod));
		unload_module(mod)
	
	# Begin ze actual loadink!
	
	theMod = __import__(mod, globals(), locals(), [], -1)
	theMod.command = lambda *a, **kw : command_mod(mod, *a, **kw)
	theMod.hook = lambda h : hook_mod(mod, h)
	theMod.logger = logging.getLogger("module.%s" % mod)
	
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
				ctx.reply("[Load Module] Error loading %s: %s" % (mod,e))
		ctx.reply("[Load Module] Done.")
	else:
		ctx.reply("[Error] Unknown 'load' sub-command: %s" % what);

@command("unload", 2)
def unload_cmd(ctx, cmd, arg, what, *args):
	"""unload module <mod1> [mod2]..."""
	if what == "module" or what == "mod":
		for mod in args:
			try:
				unload_module(mod)
			except Exception, e:
				ctx.reply("[Unload Module] Error unloading %s: %s" % (mod,e))
		ctx.reply("[Unload Module] Done.")
	else:
		ctx.reply("[Error] Unknown 'unload' sub-command: %s" % what);

@command("info", 2)
def info_cmd(ctx, cmd, arg, what, *args):
	"""info <module|command> <data>"""
	if what == "module" or what == "mod":
		ctx.reply("Information available for module %s:" % args[0])
		try:
			mod = mods[args[0]]
			doc = mod.__doc__.split("\n", 1)[0];
			if doc == "":
				doc = "*** This module doesn't provide a doc string, yell at the author."
			ctx.reply("[%s] %s" % (args[0], doc))
			try:
				info = mod.__info__
				ctx.reply("[%s] Author: %s" % (args[0], info['Author']))
				ctx.reply("[%s] Version: %s" % (args[0], info['Version']))
			except AttributeError:
				ctx.reply("[%s] Additional information not available" % args[0])
		except KeyError:
			ctx.reply("[[ Information not available as module is not loaded. ]]")
	elif what == "command" or what == "cmd":
		c = args[0]
		if c in commands:
			#ctx.reply("Info for command %s" % c)
			#ctx.reply("[%s] %d min args" % (c, c._args))
			s = "[Info] Information for command %s" % c
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

			usage = (commands[c].__doc__ or "").split("\n", 1)[0];
			if usage != "":
				s += usage
			else:
				s += "[[ No usage info given. ]]"

			ctx.reply(s)
		else:
			ctx.reply("I don't seem to have any data available for that command.")
	else:
		ctx.reply("[Error] Unknown info element: %s" % what)

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
			ctx.reply("[Error] The command %s takes atleast %d arguments, %d given." % (cmd, cmdf._min, len(args)))
		else:
			commands[cmd](ctx, cmd, arg, *args)
	else:
		fire_hook("command", ctx, cmd, arg, args)
	
@hook("message")
def command_processor(ctx, msg):
	if msg[0] == "@":
		handle_command(ctx, msg[1:])
	elif msg.startswith('%s: ' % ctx.irc.nick):
		handle_command(ctx, msg[len('%s: ' % ctx.irc.nick):]);
		
