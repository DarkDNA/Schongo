"""
Example Module to test the module loading and unloading system.
"""

def onLoad():
	@command("cheese")
	def cheese_cmd(ctx, cmd, arg, *args):
		ctx.reply("Cookies!")