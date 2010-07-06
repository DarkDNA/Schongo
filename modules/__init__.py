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

def command_mod(mod, name, args=-1):
	def retCmd(f):
		commands[name] = f;
		f._mod = mod;
		f._args = args
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
	
@command("load_module", 1)
def load_mod_cmd(ctx, cmd, arg, *args):
	for mod in args:
		try:
			load_module(mod)
		except Exception, e:
			ctx.reply("[Load Module] Error loading %s: %s" % (mod,e))
	ctx.reply("[Load Module] Done.")
	
@command("unload_module", 1)
def unload_mod_cmd(ctx, cmd, arg, *args):
	for mod in args:
		try:
			unload_module(mod)
		except Exception, e:
			ctx.reply("[Unload Module] Error unloading %s: %s" % (mod,e))
	ctx.reply("[Unload Module] Done.")
	

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
		if cmdf._args == -1:
			# Dumb command
			cmdf(ctx, cmd, arg);
		elif len(args) < cmdf._args:
			ctx.reply("[Error] The command %s takes atleast %d arguments, %d given." % (cmd, cmdf._args, len(args)))
		else:
			commands[cmd](ctx, cmd, arg, *args)
	
@hook("message")
def command_processor(ctx, msg):
	if msg[0] == "@":
		handle_command(ctx, msg[1:])
	elif msg.startswith('%s: ' % ctx.irc.nick):
		handle_command(ctx, msg[len('%s: ' % ctx.irc.nick):]);
		