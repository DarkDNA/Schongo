import locale
import subprocess as subProc
import os
import threading
import time
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

#Strips everything but letters and numbers from a string. If 'exceptions' is included as a string, any character in exceptions will be left as-is.
def stripPunctuation(str, exceptions=''):
	letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
	numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
	exceptions = exceptions.split('').extend(letters).extend(numbers)
	nstr = ''
	for char in str:
		if char in exceptions:
			nstr += char
	return nstr

#Capitalizes first letter of the string and makes the rest lower case. Does this for the first character after every space until it hits another space if atspaces is set to True.
def casecor(str, atspaces=False):
		if atspaces:
			cor = ''
			pieces = str.split(' ')
			for piece in pieces:
				cor += ' ' + piece[0:1].upper() + piece[1:].lower()
			return cor[1:]
		else:
			   return cor[0:1].upper() + cor[1:].lower()

#Properly format out a list to a string, including separating commas and 'and' before the last value if useand set to true.
def listify(list, useand=False):
	if len(list) == 1:
		return list[0]
	result = ', '.join(list)
	if useand:
		result = result[0:result.rfind(',')+2] + 'and' + result[result.rfind(',')+1:]
	return result

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