"""Example Module to test various new features as they are added.

Feel free to add to them!
"""

__info__ = {
	"Author": "Various",
	"Version": "Cake",
	"Dependencies": [
		"_timer"
	]
}

def onLoad():

	@timer(15, True)
	def bacon_timer(ctx):
		ctx.reply("Meow!")
		return True

	@timer(5)
	def delay_say_timer(ctx, msg):
		ctx.reply(msg)

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

	@command("test timer delay")
	def delay_cmd(ctx, cmd, arg):
		delay_say_timer.start(ctx, arg)

	@command("test crash")
	def crash_cmd(ctx, cmd, arg):
		None.dicks()

	@command("test userinfo")
	def userinfo_cmd(ctx, cmd, arg):
		ctx.reply(get_user_info(ctx, arg).HostName)

	@command("test chaninfo")
	def chaninfo_cmd(ctx, cmd, arg):
		chan = get_channel_info(ctx, arg)

		ctx.reply("Users: %s" % ', '.join(chan.Users))
		ctx.reply("Topic: %s" % chan.Topic)

	@command("test say", 2)
	def say_cmd(ctx, cmd, arg, *args):
		where, what = arg.split(' ', 1)
		IrcContext.fromString(where, ctx).reply("Ohai from %s! %s" % ( ctx.chan, what))

	@hook("message")
	def crash_hook(ctx, msg):
		if msg == "CRASH":
			None.dicks()

	@hook("join")
	def join_hook(ctx):
		if ctx.chan == "#schongo-dev":
			ctx.reply("Welcome!")
	
	@hook("topic")
	def topic_hook(ctx, topic):
		ctx.reply("%s is a topic changin bitch!" % ctx.who.nick, "Topic Alarm")
	
	
