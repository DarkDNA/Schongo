"""
Used to run processes and keep the main module free to do other things.
Unfortunately this thread is designed to work under unix based systems so...
Sorry windows users :/
"""
import subprocess as subProc
import os
import threading

class procThread(threading.Thread):
	context = None 
	proc = None 
	procCommand = None 
	
	def __init__(self, procCommand, ctx):
		threading.Thread.__init__(self)
		self.procCommand = procCommand
		self.context = ctx
		
		
	def run(self):
		if self.procCommand is not None:
			self.proc = subProc.Popen(self.procCommand, stdin=subProc.PIPE, stdout=subProc.PIPE, stderr=subProc.STDOUT)
			for line in self.proc.stdout:
				if line is not None and line != "\n":
					print '\'%s\'' % line
					self.context.reply(line.strip(),self.procCommand[0])
			
			
		else:
			self.context.reply("Error running process", "procThread")
		
	def endProc(ctx):
		os.kill(self.proc.pid, signal.CTRL_C_EVENT)
		ctx.reply("Killed process", self.procCommand[0])
		