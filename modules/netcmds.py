"""
Module that wraps around ping and traceroute. 
The new and improved system uses a new threading technique to handle unix commands
"""
import procThread
import threading
__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.1",
	"Dependencies": ["ping", "traceroute"]
}
def onLoad():
	
	@command("ping", 1)
	def ping(ctx, cmd, arg, *args):
		address = args[0]
		shellCmd = ["ping", "-c", "5", address]
		pt = procThread.procThread(shellCmd, ctx)
		pt.start()
		
	@command(["traceroute", "tr", "tracert"], 1)
	def tracert(ctx, cmd, arg, *args):
		address = args[0]
		shellCmd = []
		if os.name == 'nt':
			shellCmd = ["tracert", address]
			rocess = subprocess.Popen(shellCmd, stdin=MODIFIED_subprocess.PIPE, stdout=MODIFIED_subprocess.PIPE, stderr=MODIFIED_subprocess.STDOUT)
			output = process.communicate()
			listOut = list(output)
			for l in listOut:	
				if l != None:
					ctx.reply(l, "TraceRoute")
			
		else:
			shellCmd = ["traceroute", address]
			pt = procThread.procThread(shellCmd, ctx)
			pt.start()
			
