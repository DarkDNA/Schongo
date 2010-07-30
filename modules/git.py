"""Module to handle git pull for the bot. This enables the users in IRC to update the bot without having to mess with the command line"""
import procThread

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": ["Git"]
}
def onLoad():

	@command("git")	
	def git(ctx, arg, *args):
		shellCommand = ["git"]
		shellCommand.extend(args)
		print shellCommand
		pt = procThread.procThread(shellCommand,ctx)
		pt.start()