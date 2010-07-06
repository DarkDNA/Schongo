from random import choice

def onLoad():
	@command("choice")
	def choice_cmd(ctx, cmd, arg):
		ctx.reply("%s: %s" % (ctx.who.nick, choice(arg.split('or'))))