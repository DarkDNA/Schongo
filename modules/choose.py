"""Provides some random commands."""
from random import choice

def onLoad():
	@command("choose")
	def choose_cmd(ctx, cmd, arg):
		"""choose one or two or ... or n
Picks from the given options - options are seperated by the string ' or '"""
		ctx.reply("%s: %s" % (ctx.who.nick, choice(arg.split(' or ')).strip()))
	
	@command("8ball")
	def eightball_cmd(ctx, cmd, arg):
		"""8ball <life questions of great importance>
Shakes the bot's built-in ( Free of charge! ) eight ball, and outputs the result"""
		ctx.reply("%s: %s" % (ctx.who.nick, choice((
			'Yes', 'No', 'Outlook hazy, ask again later',
			'Maybe', 'Computer says no.'))))
