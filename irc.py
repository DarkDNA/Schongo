import socket
from threading import Thread;


class IrcOrigin:
	nick = None
	ident = None
	host = None
	
	def __init__(self, hostmask):
		#self.nick, data = hostmask.split('!', 1)
		#self.ident, self.host = data.split('@')
		parts = hostmask.split('!', 1)
		self.nick = parts[0]
		if len(parts) > 1:
			self.ident, self.host = parts[1].split('@')
		
	def __str__(self):
		return "%s!%s@%s" % (self.nick, self.ident, self.host)

class IrcMessage:
	"""Holds the meta info for an IRC Message"""
	origin = None
	command = None
	args = None
# This parses the raw IRC Protocol and breaks it down into seperate events
# This allows us to seperate the protocol structure from the logic
class IrcSocket(Thread):
	"""Parses the Raw IRC Protocol and breaks it down into events, very low-level"""
	_socket = None
	_server = None
	_port = 6667
	connected = False
	
	
	def __init__(self, server=None, port=6667):
		Thread.__init__(self)
		
		if server is not None:
			self._server = server
		self._port = port
		
	def connect(self):
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self._socket.connect((self._server, self._port))
		except socket.error, message:
			print("!!! Could not connect: %s" % message)
			return

		self.connected = True
		
		self.onConnected()
		
		
	def disconnect(self, reason=None):
		pass
		
	def sendMessage(self, *msg, **kwargs):

		if not self.connected:
			return # Throw an error?
			
		line = ""
		if 'origin' in kwargs:
			line += ":" + kwargs['origin']
		line += ' '.join(msg) 
		if 'end' in kwargs:
			line += " :" + kwargs['end']
				
		print("<=" + line);
		
		line += "\r\n"
		
		self._socket.send(line)
	
	def run(self):
		if not self.connected:
			self.connect()
		buffer = ""
		while True:
			data = 0
			try:
				data = self._socket.recv(512)
			except socket.error:
				pass
			if data is 0 or not self.connected:
				self.onDisconnected()
				return
			data = (buffer + data).split("\n")
			buffer = data.pop()
			for line in data:
				line = line.strip()
				print("=>" + line);
				self.onLine(line)
	
	def onLine(self, line):
		msg = IrcMessage()
		if line[0] == ':':
			msg.origin, line = line[1:].split(' ', 1)
			msg.origin = IrcOrigin(msg.origin)
		
		parts = line.split(' :', 1)
		args = parts[0].split(' ')
		msg.command = args[0]
		msg.args = args[1:]
		if len(parts) > 1:
			msg.args.append(parts[1])
		
		self.onMessage(msg)
		
		hook = None
		try:
			hook = getattr(self, "on" + msg.command)
		except AttributeError:
			pass
			
		if hook is not None:
			hook(self, msg)
			
	def onMessage(self, msg):
		if msg.command == "PING":
			sendMessage("PONG", end=msg.args[0])
			
	def onConnected(self):
		pass
	
	def onDisconnected(self):
		pass
			
			
class IrcClient(IrcSocket):
	nicks = []
	nick = None
	_nickPos = 0
	realname = None
	ident = None
	
	# TODO: Track channels and people
	
	def __init__(self, server=None, port=6667, nicks=None, ident=None, realname=None):
		IrcSocket.__init__(self, server, port)
		
		if nicks is not None:
			self.nicks = nicks
			
		if realname is not None:
			self.realname = realname
		
		if ident is not None:
			self.ident = ident

	# Our API.
	
	def join(self, channel, password=None):
		if password is not None:
			self.sendMessage("JOIN", channel, password)
		else:
			self.sendMessage("JOIN", channel)
	
	def say(self, channel, msg):
		self.sendMessage("PRIVMSG", channel, end=msg)
	
	def part(self, channel, reason=None):
		self.sendMessage("PART", channel, end=reason)
		
	def disconnect(self, reason=None):
		self.sendMessage("QUIT", end=reason)
		super.disconnect(self, reason)
		
	# Overwritten events
			
	
	def onConnected(self):
		print("@@@ Coookies");
		self.nick = self.nicks[0]
		self._nickPos = 0
		self.sendMessage("USER", self.ident, "8", "*", end=self.realname)
		self.sendMessage("NICK", self.nick)
		
	
		
		
	# Our events
	
	def onNickChange(self, newnick):
		pass
	
	
	# IRC Events
	
	def onMessage(self, msg):
		if msg.command == "NICK":
			if msg.origin.nick == self.nick:
				self.nick = msg.args[0]
				self.onNickChange(nick)
		elif msg.command == "443":
			self._nickPos += 1
			if self._nickPos > len(self.nicks):
				self.disconnect("No nicks Left")
			self.nick = self.nicks[self._nickPos]
			self.sendMessage("NICK", self.nick)
		else:
			IrcSocket.onMessage(self, msg)
	