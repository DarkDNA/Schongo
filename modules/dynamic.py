cmds = {}

def onLoad():
	@command("add")
	def add_command(ctx, cmd, arg):
		dcmd, val = arg.split(' ', 1)
		cmds[dcmd] = val

	@command("delete", 1)
	def del_command(ctx, cmd, arg, dcmd):
		del cmds[dcmd]

	@hook("command")
	def command_hook(ctx, cmd, arg, args):
		if cmd in cmds:
			ctx.reply(cmds[cmd])
