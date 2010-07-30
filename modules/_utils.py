import locale
import subprocess as subProc
import os
import threading
locale.setlocale(locale.LC_ALL, "")

def prettyNumber(num):
	return locale.format("%d", int(num), 1)

def prettyTime(secs):
	if not isinstance(secs, int):
		secs = int(secs)
	mins = secs // 60
	hours = mins // 60 # There are actualy some hour+ long youtube videos

	secs = secs % 60
	mins = mins % 60

	time = "%02d:%02d" % (mins, secs)

	if hours > 0:
		time = "%d:%s" % (hours, time)

	return time

class procThread(threading.Thread):
	context = None
	proc = None
	procCmd = None #this is a list, the way the subprocess works is via a list of arguments so this is easiest to work with
	
	def __init__(self, cmd, ctx):
		threading.Thread.__init__(self)
		self.procCmd = cmd
		self.context = ctx
	
	def run(self):
		if self.procCmd is not None:
			self.proc = subProc.Popen(self.procCmd, stdin=subProc.PIPE, stdout=subProc.PIPE, stderr=subProc.STDOUT)
			for line in self.proc.stdout:
				if line is not None and line != "\n":#ignore the new lines as they cause annoyances in IRC
					self.context.reply(line.strip(),self.procCmd[0]) #send the stripped line to IRC
			
			
		else:
			self.context.reply("Error running process", "procThread")
			
	def endProc(ctx):
		os.kill(self.proc.pid, signal.CTRL_C_EVENT)
		ctx.reply("Killed process", self.procCommand[0])