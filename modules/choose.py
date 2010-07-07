"""Provides some random commands."""
from random import choice

def onLoad():
	@command("choose")
	def choose_cmd(ctx, cmd, arg):
		ctx.reply("%s: %s" % (ctx.who.nick, choice(arg.split('or')).strip()))
	
	@command("8ball")
	def eightball_cmd(ctx, cmd, arg):
		ctx.reply("%s: %s" % (ctx.who.nick, choice((
			'Yes', 'No', 'Outlook hazy, ask again later',
			'Maybe', 'Computer says no.'))))