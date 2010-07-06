from random import choice

def onLoad():
	@command("choose")
	def choose_cmd(ctx, cmd, arg):
		ctx.reply("%s: %s" % (ctx.who.nick, choice(arg.split('or')).strip()))