"""Provides remote-control functionality to Schongo
"""

def onLoad():
	@command("ping")
	def ping_cmd(ctx, cmd, arg):
		ctx.reply("Pong!")

	@privs(2)
	@command("say")
	def say_cmd(ctx, cmd, arg):
		ctx.reply(arg)
	
	@privs(5)
	@command("eval")
	def eval_cmd(ctx, cmd, arg):
		exec(arg)
