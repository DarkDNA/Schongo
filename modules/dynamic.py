"""Provides Dynamic commands to Schongo

Dynamic commands can use special syntax enhancements, such as %%Nick%% to refer to the person's nick, or %%Channel%% The syntax is as follows:

%%Variable%% - Replaced with the value of Variable
%[function name][function args]% - Dynamic function, such as random

== TODO ==
+ Implement the ability for other plugins to define functions and variables

"""

import re
import random

# ----------------------- Meta Info -------

__info__ = {
	"Author": "Amanda Cameron",
	"Version": "0.1a",
	"Dependencies": [
		"_persist"
	]
}


__persist__ = [ "cmds" ]

# ------------------------ Data for us ----

functions = {}
cmds = {}

def onLoad():
	addCommands()
	addHooks()

def addCommands():

	@command("add")
	def add_command(ctx, cmd, arg):
		dcmd, val = arg.split(' ', 1)
		cmds[dcmd] = val
		ctx.reply("Added command %s" % dcmd)

	@command("delete", 1)
	def del_command(ctx, cmd, arg, dcmd):
		del cmds[dcmd]
		ctx.reply("Deleted command %s" % dcmd)

	@command("source", 1)
	def source_command(ctx, cmd, arg, dcmd):
		if dcmd in cmds:
			ctx.reply(cmds[dcmd], dcmd, False)
		else:
			ctx.error("No such command: %s" % dcmd)

	@command("say")
	def say_command(ctx, cmd, arg):
		sendMessage(ctx, arg)

def addHooks():

	@hook("command")
	def command_hook(ctx, cmd, arg, args):
		if cmd in cmds:
			#ctx.reply(cmds[cmd])
			sendMessage(ctx, cmds[cmd])

#------------------------------------------

def sendMessage(ctx, message, **kwargs):
	ctx.reply(parseDynamic(ctx, message, **kwargs))

# ------------------------ Parser ---------

class ParseContext(dict):
	values = {}
	context = None

	
	def __init__(self, context, values={}):
		self.context = context
		self.values = values

		self["Channel"] = context.chan
		self["Nick"] = context.who.nick

	# Magic to let us access the variables using the [] operators

	def __getitem__(self, key):
		if key in self.values:
			return self.values[key]
		return None

	def __setitem__(self, key, val):
		self.values[key] = val

	def __delitem__(self, key):
		del self.values[key]
	
	def __contains__(self, key):
		return key in self.values

varRegEx = re.compile("%%([A-Za-z0-9]+)%%")
funcRegEx = re.compile("%\\[([a-z]+)\\]\\[(.+)\\]%")


def parseDynamic(ctx, message, **kwargs):

	if not isinstance(ctx, ParseContext):
		ctx = ParseContext(ctx, kwargs)

	def replaceVariable(m):
		var = m.group(1)
		return ctx[var] or ("[[ Unknown Variable %s ]]" % var)

	def replaceFunction(m):
		func = m.group(1)
		arg = m.group(2)
	
		f = getFunction(func)

		if f is None:
			return "[[ Unknown function %s ]]" % func
		else:
			return f(ctx, func, arg)

	message = varRegEx.sub(replaceVariable, message)
	message = funcRegEx.sub(replaceFunction, message)

	return message

def getFunction(func):
	if func in functions:
		return functions[func]

	return None

# --------------- Defining Elements -------


def dynFunction(name):
	""" Defines a dynamic function of the form func(context, function name, arg)"""
	def funcRet(f):
		functions[name] = f
	return funcRet


# ------------------------------------------

@dynFunction("random")
def random_func(ctx, func, arg):
	""" returns a random option from the given parameters

	Examples:
	%[random][1:4]% - returns a random number from one to four
	%[random][a||b||c]% returns a or b or c"""
	parts = arg.split('||')
	if len(parts) == 1:
		parts = parts[0].split(':')
		try:
			return "%d" % random.randrange(int(parts[0]), int(parts[1]))
		except:
			return "[[ Must be numbers! ]]"
	else:
		return random.choice(parts)
