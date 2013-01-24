import socket
import logging
import ssl
from threading import Thread


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


	def __init__(self, server, port=6667):
		Thread.__init__(self, name="IrcSocket(%s)" % server)

		self._server = server
		self._port = port
		if self._server.startswith('+'):
			self._server = self._server[1:]
			self.ssl = True
		self.logger = logging.getLogger("IrcSocket(%s)" % self._server)

	def connect(self):

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		if self.ssl:
			self._socket = ssl.wrap_socket(self._socket)
		try:
			self._socket.connect((self._server, self._port))
		except socket.error as message:
			#print("!!! Could not connect: %s" % message)
			self.logger.error("Could not connect: %s" % message)
			return

		self.connected = True


	def disconnect(self, reason=None):
		self._socket.close()
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

		#print("<=" + line);
		self.logger.debug("<= %s" % line)

		line += "\r\n"

		line = line.encode('utf-8')

		self._socket.send(line)

	def run(self):
		if not self.connected:
			self.connect()
		buffer = ""
		while True:

			try:
				data = self._socket.recv(512)
				try:
					data = data.decode("utf-8")
				except UnicodeDecodeError:
					try:
						data = data.decode("ascii")
					except UnicodeDecodeError:
						self.logger.error("Couldn't decode line %s", data)
						data = " "
			except socket.error:
				data = ""

			if data == "" or not self.connected:
				self.onDisconnected()
				return

			data = (buffer + data).split("\n")
			buffer = data.pop()
			for line in data:
				line = line.strip()
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
	channels = {}

	# TODO: Track channels and people

	def __init__(self, server=None, port=6667, nicks=None, ident=None, realname=None):
		IrcSocket.__init__(self, server, port)

		if nicks is not None:
			self.nicks = nicks

		if realname is not None:
			self.realname = realname

		if ident is not None:
			self.ident = ident

		self.supportsData = {}

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

	def part_channel(self, channel, reason="Bye!"):
		self.sendMessage("PART", channel, end=reason)

	def setTopic(self, channel, topic):
		self.sendMessage("TOPIC", channel, end=topic)

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

	def onJoin(self, who, chan):
		pass

	def onPart(self, who, chan, message):
		pass

	def onQuit(self, who, message):
		pass

	def onTopic(self, who, chan, topic):
		pass

	def onMode(self, who, chan, modes, values):
		pass

	def onNotice(self, target, who, message):
		pass


	# IRC Events

	SUPPORT_INTS = ['NICKLEN', 'CHANNELLEN', 'AWAYLEN',
					'TOPICLEN', 'KICKLEN', 'MAXCHANNELS',
					'WATCH', 'SILENCE', 'MODES', 'MAXTARGETS']

	SUPPORT_LISTS = ['CHANMODES', 'CMDS']

	def _iSupport(self, what):
		for i in what:
			if '=' in i:
				name, value = i.split('=', 2)
				value = self._supportValue(name, value)
				self.supportsData[name] = value
			else:
				self.supportsData[i] = True

	def _supportValue(self, name, value):

		if name in self.SUPPORT_INTS:
			return int(value)
		if name in self.SUPPORT_LISTS:
			return value.split(',')

		return value

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
		elif msg.command == "NOTICE":
			target = msg.args[0]
			message = msg.args[1]
			if message.startswith("\x01") and message.endswith("\x01"):
				body = message[1:-1];
				parts = body.split(' ', 1)
				cmd = parts[0]
				if len(parts) > 1:
					arg = parts[1]
				else:
					arg = None

				self.onCtcp(target, msg.origin, cmd, arg)
			else:
				self.onNotice(target, msg.origin, message)

		elif msg.command == "PRIVMSG":
			channel = msg.args[0]
			message = msg.args[1]

			if message.startswith("\x01") and message.endswith("\x01"):
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
			else:
				self.onMsg(channel, msg.origin, message)
		elif msg.command == "JOIN":
			channel = msg.args[0]
			self.onJoin(msg.origin, channel)
		elif msg.command == "PART":
			channel = msg.args[0]
			message = msg.args[1] if len(msg.args) > 1 else ""
			self.onPart(msg.origin, channel, message)
		elif msg.command == "QUIT":
			message = msg.args[0] if len(msg.args) > 0 else ""
			self.onQuit(msg.origin, message)
		elif msg.command == "001":
			# We've successfuly connected, partay!
			self.onConnected()
		elif msg.command == "005":
			self._iSupport(msg.args[0:-2])
		elif msg.command == "TOPIC":
			channel = msg.args[0]
			topic = msg.args[1]
			self.onTopic(msg.origin,channel,topic)
		elif msg.command == "332":
			channel = msg.args[1]
			topic = msg.args[2]
			self.onTopic(None, channel, topic)
		elif msg.command == "MODE":
			channel = msg.args[0]
			modes = msg.args[1]
			values = msg.args[2:]
			self.onMode(msg.origin, channel, modes, values)
		else:
			IrcSocket.onMessage(self, msg)
