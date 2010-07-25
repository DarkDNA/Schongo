import socket
from threading import Thread;
import logging

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
	logger = None
	
	
	def __init__(self, server=None, port=6667):
		Thread.__init__(self)
		
		if server is not None:
			self._server = server
		self._port = port
		
		self.logger = logging.getLogger("IrcSocket")
		
	def connect(self):
		
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self._socket.connect((self._server, self._port))
		except socket.error, message:
			#print("!!! Could not connect: %s" % message)
			self.logger.error("Could not connect: %s" % message)
			return

		self.connected = True
		
		self.onConnected()
		
		
	def disconnect(self, reason=None):
		self._socket.close()
		pass
    
	def msgFormat(self, msg):
		fmtchars = {
        '`B':u'\u0002',
        '`U':u'\u0001',
        '`R':u'\u0016'}
        off = '\u000F'
    
	def sendMessage(self, *msg, **kwargs):

		if not self.connected:
			return # Throw an error?
			
		line = ""
		if 'origin' in kwargs:
			line += ":" + kwargs['origin']
		line += ' '.join(msg) 
		if 'end' in kwargs:
			line += " :" + kwargs['end']
				
		#print("<=" + line);
		self.logger.debug("<= %s" % line)
		
		line += "\r\n"
		
		try:
			line = line.encode('utf-8')
		except UnicodeEncodeError, error:
			logger.warn('Could not encode UTF-8 string sent to socket: %s' % error)
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
			if data == 0 or not self.connected:
				self.onDisconnected()
				return
			data = (buffer + data).split("\n")
			buffer = data.pop()
			for line in data:
				line = line.strip()
				try:
					line = line.decode('utf-8')
				except UnicodeDecodeError, error:
					logger.warn('Could not decode UTF-8 string sent by socket: %s' % error)
				#print("=>" + line);
				self.logger.debug("=> %s" % line)
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
			self.sendMessage("PONG", end=msg.args[0])
			
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
	
	def join_channel(self, channel, password=None):
		if password is not None:
			self.sendMessage("JOIN", channel, password)
		else:
			self.sendMessage("JOIN", channel)
	
	def say(self, channel, msg):
		self.sendMessage("PRIVMSG", channel, end=msg)
		
	def notice(self, target, msg):
		self.sendMessage("NOTICE", target, end=msg)
	
	def part_channel(self, channel, reason=None):
		self.sendMessage("PART", channel, end=reason)
		
	def disconnect(self, reason=None):
		self.sendMessage("QUIT", end=reason)
		IrcSocket.disconnect(self, reason)
		
	def connect(self):
		IrcSocket.connect(self)
		self.nick = self.nicks[0]
		self._nickPos = 0
		self.sendMessage("USER", self.ident, "8", "*", end=self.realname)
		self.sendMessage("NICK", self.nick)
		
		
	# Our events
	
	def onNickChange(self, newnick):
		pass
		
	def onNick(self, old, new):
		pass
	
	def onMsg(self, chan, who, what):
		pass
	
	def onAction(self, chan, who, what):
		pass
	
	
	# IRC Events
	
	def onMessage(self, msg):
		if msg.command == "NICK":
			if msg.origin.nick == self.nick:
				self.nick = msg.args[0]
				self.onNickChange(self.nick)
			else:
				self.onNick(msg.origin, msg.args[0])
		elif msg.command == "433":
			self._nickPos += 1
			if self._nickPos > len(self.nicks):
				self.disconnect("No nicks Left")
			self.nick = self.nicks[self._nickPos]
			self.sendMessage("NICK", self.nick)
		elif msg.command == "PRIVMSG":
			channel = msg.args[0]
			message = msg.args[1]
			if message[0] == "\x01" and message[-1] == "\x01":
				body = message[1:-1];
				parts = body.split(' ', 1)
				cmd = parts[0]
				if len(parts) > 1:
					arg = parts[1]
				else:
					arg = None
				if cmd == "ACTION":
					self.onAction(channel, msg.origin, arg)
				else:
					self.onCtcp(channel, msg.origin, cmd, arg)
			self.onMsg(channel, msg.origin, message)
		elif msg.command == "001":
			# We've successfuly connected, partay!
			self.onConnected()
		else:
			IrcSocket.onMessage(self, msg)
	
