_hooks = {}
_ircCommands = {}


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
		
def fire_hook(hook, *args):
	if hook in _hooks:
		for h in _hooks[hook]:
			h(*args)
	

# Decorators

def command(name):
	def retCmd(f):
		global _ircCommands;
		_ircCommands[name] = f;
		return f
	return retCmd

def hook(hook):
	def retHook(f):
		global _hooks;
		if hook in _hooks:
			_hooks[hook].append(f)
		else:
			_hooks[hook] = [ f ]
		return f
	return retHook	
# Core Code

@command("ping")
def ping_cmd(ctx, cmd, args):
	ctx.reply("Pong!")

@command("say")
def say_cmd(ctx, cmd, args):
	ctx.reply(' '.join(args))
	
@command("shutdown")
def shutdown_cmd(ctx, cmd, args):
	ctx.irc.disconnect(' '.join(args))
	
@hook("message")
def command_processor(ctx, msg):
	if msg[0] == "@":
		parts = msg[1:].split(' ')
		cmd = parts[0]
		args = parts[1:]
		if cmd in _ircCommands:
			_ircCommands[cmd](ctx, cmd, args)