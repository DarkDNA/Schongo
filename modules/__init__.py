import sys

commands = {}
hooks = {}
mods = {}

class IrcContext:
	""" Holds three important context things, and provides some helper methods."""
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

# Commands
		
def fire_hook(hook, *args, **kw):
	if hook in hooks:
		for m in hooks[hook]:
			hooks[hook][m](*args, **kw)
	
def load_module(mod):
	if mod in mods:
		print("@@@ Module `%s' already loaded" % mod)
		unload_module(mod)
	
	# Begin ze actual loadink!
	
	theMod = __import__(mod, globals(), locals(), [], -1)
	theMod.command = lambda cmd : command_mod(mod, cmd)
	theMod.hook = lambda h : hook_mod(mod, h)
	
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

def command_mod(mod, name):
	def retCmd(f):
		commands[name] = f;
		f._mod = mod;
		return f
	return retCmd

def hook_mod(mod, hook):
	def retHook(f):
		if hook not in hooks:
			hooks[hook] = {}
		hooks[hook][mod] = f
		return f
	return retHook	

command = lambda c : command_mod("__init__", c)
hook = lambda c : hook_mod("__init__", c)
	
# Core Code
	
@command("load_module")
def load_mod_cmd(ctx, cmd, arg, *args):
	for mod in args:
		try:
			load_module(mod)
		except Exception, e:
			ctx.reply("[Load Module] Error loading %s: %s" % (mod,e))
	ctx.reply("[Load Module] Done.")
	
@command("unload_module")
def unload_mod_cmd(ctx, cmd, arg, *args):
	for mod in args:
		try:
			unload_module(mod)
		except Exception, e:
			ctx.reply("[Unload Module] Error unloading %s: %s" % (mod,e))
	ctx.reply("[Unload Module] Done.")
	

	
@hook("message")
def command_processor(ctx, msg):
	if msg[0] == "@":
		parts = msg[1:].split(' ',1)
		cmd = parts[0]
		if len(parts) > 1:
			arg = parts[1]
		else:
			arg = ""
		args = arg.split(' ')
		if cmd in commands:
			commands[cmd](ctx, cmd, arg, *args)