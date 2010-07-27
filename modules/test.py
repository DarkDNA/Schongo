"""Example Module to test various new features as they are added.

Feel free to add to them!
"""

def onLoad():

	@timer(15, True)
	def bacon_timer(ctx):
		ctx.reply("Meow!")

	parent_cmd("test")
	parent_cmd("test timer")

	@command("test timer start")
	def cheese_cmd(ctx, cmd, arg, *args):
		ctx.reply("I'm hungry...")
		bacon_timer.start(ctx)

	@command("test timer stop")
	def catnip_cmd(ctx, cmd, arg):
		ctx.reply("Ohh. *nom*")
		bacon_timer.cancel()

