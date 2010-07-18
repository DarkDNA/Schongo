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

	@command("source", 1)
	def source_command(ctx, cmd, arg, dcmd):
		if dcmd in cmds:
			ctx.reply(cmds[dcmd], dcmd, False)
		else:
			ctx.error("No such command: %s" % dcmd)

def addHooks():
	@hook("command")
	def command_hook(ctx, cmd, arg, args):
		if cmd in cmds:
			ctx.reply(cmds[cmd])
