"""
Module that wraps around ping and traceroute
"""
import MODIFIED_subprocess
import os
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": ["ping", "traceroute"]
}
def onLoad():
	
	@command("ping", 1)
	def ping(ctx, cmd, arg, *args):
		address = args[0]
		shellCmd = ["ping", "-c", "5", address]
		process = MODIFIED_subprocess.Popen(shellCmd, stdin=MODIFIED_subprocess.PIPE, stdout=MODIFIED_subprocess.PIPE, stderr=MODIFIED_subprocess.STDOUT)
		output = process.communicate()
		listOut = list(output)
		for l in listOut:
			if l != None:
				ctx.reply(l,"Ping")
		
	@command(["traceroute", "tr", "tracert"], 1)
	def tracert(ctx, cmd, arg, *args):
		address = args[0]
		shellCmd = []
		if os.name == 'nt':
			shellCmd = ["tracert", address]
		else:
			shellCmd = ["traceroute", address]
		
		process = MODIFIED_subprocess.Popen(shellCmd, stdin=MODIFIED_subprocess.PIPE, stdout=MODIFIED_subprocess.PIPE, stderr=MODIFIED_subprocess.STDOUT)
		output = process.communicate()
		listOut = list(output)
		for l in listOut:	
			if l != None:
				ctx.reply(l, "TraceRoute")
			
