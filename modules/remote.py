"""
Provides remote-control functionality to Schongo
"""

def onLoad():
	@command("ping")
	def ping_cmd(ctx, cmd, arg):
		ctx.reply("Pong!")

	@command("say")
	def say_cmd(ctx, cmd, arg):
		ctx.reply(arg)
	
	@command("hello", 1)
	def hello_cmd(ctx, cmd, arg, who):
		ctx.reply("Hello, %s!" % who)
		
	@command("shutdown")
	def shutdown_cmd(ctx, cmd, arg):
		ctx.irc.disconnect(arg)
		
	@command("eval")
	def eval_cmd(ctx, cmd, arg):
		exec arg