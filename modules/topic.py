# coding 
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

def onLoad():
	
	@command("topic",1)
	def topic_command(ctx, cmd, arg, *args):
		ctx.irc.setTopic(ctx.chan, ' '.join(args))