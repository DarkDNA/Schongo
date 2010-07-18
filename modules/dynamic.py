"""Provides Dynamic commands to Schongo"""

__info__ = {
	"Author": "Selig Arkin",
	"Version": "0.1a",
	"Dependencies": []
}

cmds = {}

def onLoad():
	addCommands()
	addHooks()

def addCommands():
	@command("add")
	def add_command(ctx, cmd, arg):
		dcmd, val = arg.split(' ', 1)
		cmds[dcmd] = val
		ctx.reply("Added command %s" % dcmd)

	@command("delete", 1)
	def del_command(ctx, cmd, arg, dcmd):
		del cmds[dcmd]
		ctx.reply("Deleted command %s" % dcmd)

def addHooks():
	@hook("command")
	def command_hook(ctx, cmd, arg, args):
		if cmd in cmds:
			ctx.reply(cmds[cmd])
