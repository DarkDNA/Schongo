"""
Module that wraps around ping and traceroute. 
The new and improved system uses a new threading technique to handle unix commands
"""
import _utils
import threading
import os
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1",
	"Dependencies": ["ping", "traceroute"]
}
def onLoad():
	
	@command("ping", 1)
	def ping(ctx, cmd, arg, *args):
		"""This command runs the ping command via the command line and outputs the results into irc"""
		address = args[0]
		shellCmd = ["ping", "-c", "5", address]
		pt = _utils.procThread(shellCmd, ctx, None)
		pt.start()
		
	@command(["traceroute", "tr", "tracert"], 1)
	def tracert(ctx, cmd, arg, *args):
		"""Run traceroute or tracrt depending on system. Gets the route and timing to an IP address or domain name"""
		address = args[0]
		shellCmd = []
		if os.name == 'nt':
			logger.debug("Windows Based System Detected")
			shellCmd = ["tracert", address]
			process = subprocess.Popen(shellCmd, stdin=MODIFIED_subprocess.PIPE, stdout=MODIFIED_subprocess.PIPE, stderr=MODIFIED_subprocess.STDOUT)
			output = process.communicate()
			listOut = list(output)
			for l in listOut:	
				if l != None:
					ctx.reply(l, "TraceRoute")
			
		else:
			logger.debug("Unix based system detected: %s" % os.name)
			shellCmd = ["traceroute", address]
			pt = _utils.procThread(shellCmd, ctx, [' * * *'])
			pt.start()
			
