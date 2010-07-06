"""
Provides remote-control functionality to Schongo
"""

def onLoad():
	@command("ping")
	def ping_cmd(ctx, cmd, args):
		ctx.reply("Pong!")

	@command("say")
	def say_cmd(ctx, cmd, arg, *args):
		ctx.reply(arg)
		
	@command("shutdown")
	def shutdown_cmd(ctx, cmd, arg, *args):
		ctx.irc.disconnect(arg)