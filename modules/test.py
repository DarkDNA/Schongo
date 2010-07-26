"""
Example Module to test the module loading and unloading system.
"""

def onLoad():

	@timer(15, True)
	def bacon_timer(ctx):
		ctx.reply("Meow!")

	@command("cheese")
	def cheese_cmd(ctx, cmd, arg, *args):
		ctx.reply("Speaking again every 15s")
		bacon_timer.start(ctx)

	@command("catnip")
	def catnip_cmd(ctx, cmd, arg):
		ctx.reply("Ohh. *nom*")
		bacon_timer.cancel()
		

