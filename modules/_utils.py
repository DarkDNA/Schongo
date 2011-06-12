import locale
import subprocess as subProc
import os
import threading
import time
import htmllib
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

def stripPunctuation(str, exceptions=''):
	"""Strips everything but letters and numbers from a string. If 'exceptions' is included as a string, any character in exceptions will be left as-is."""

	letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
	
	exceptions = list(exceptions) + letters + numbers

	nstr = ''
	for char in str:
		if char in exceptions:
			nstr += char
	return nstr

def listify(list, useand=False):
	"""Properly format out a list to a string, including separating commas and 'and' before the last value if useand set to true."""

	if len(list) == 1:
		return list[0]

	if useand:
		result = "%s and %s" % (', '.join(list[:-1]), list[-1])
	else:
		result = ', '.join(list)

	return result

def unescapeHtml(html):
	p = htmllib.HTMLParser(None)
	p.save_bgn()
	p.feed(html)
	return p.save_end()

class procThread(threading.Thread):
	context = None
	proc = None
	procCmd = None #this is a list
	ignoreList = None #used to strip specified characters from the return
	
	def __init__(self, cmd, ctx, ignore):
		threading.Thread.__init__(self)
		self.procCmd = cmd
		self.context = ctx
		self.ignoreList = ignore
	
	def run(self):
		if self.procCmd is not None:			
			self.proc = subProc.Popen(self.procCmd, 
				stdin=subProc.PIPE, 
				stdout=subProc.PIPE, 
				stderr=subProc.STDOUT)
			for line in self.proc.stdout:#cycle through the output
				if self.ignoreList is not None:
					for ignore in self.ignoreList:#strip all specified chars out
						if ignore in line and ignore is not None:
							line.replace(ignore, '')
				if line != ' ' and line != None and line != '' and line != '\n' and ' * * *' not in line:
					self.context.reply(line.strip(),self.procCmd[0]) #send the stripped line to IRC
					time.sleep(2)
			
			
		else:
			self.context.reply("Error running process", "procThread")
			
	def endProc(ctx):
		os.kill(self.proc.pid, signal.CTRL_C_EVENT)
		ctx.reply("Killed process", self.procCommand[0])

	def send_input(self, line):
			self.proc.stdin.write(line)
