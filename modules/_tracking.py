"""_tracking.py is a module, auto-loaded by the core, to give Schongo the ability to keep track of people's hosts and nick changes"""

# Holds data in the following tree:

# Network -> Channel/User -> Data

# Channels contain:
#    Users    ( List of user nicks )
#    Modes    ( list of mode, value tuple )
#    Owners   ( User Nicks )
#    Ops      ( User Nicks )
#    Voiced   ( User Nicks )
#    Admins   ( User Nicks )
#    HalfOps  ( User Nicks )
#    Topic    ( Channel topic )

# Users contain:
#    Host mask
#    Channels ( List of channel names )
#    Real name ( If available )
#    Server they reside on ( If available )

global trackingData

trackingData = {}

class ChannelInfo:
	Users   = []
	Topic   = ""

	## TODO: Mode Tracking

	Modes   = []
	Owners  = []
	Admins  = []
	Ops     = []
	HalfOps = []
	Voiced  = []

	def __init__(self):
		self.Users = []
		self.Topic = ""
	
	def __str__(self):
		return "[[ ChannelInfo - Users: %s - Topic: %s ]]" % (self.Users, self.Topic)

class UserInfo:
	Channels = []
	RealName = ""
	Server = ""
	ServerHops = 0
	Ident = ""
	HostName = ""

	def __init__(self):
		self.Channels = []
		self.RealName = ""
		self.Server = ""
		self.ServerHops = 0
		self.Ident = ""
		self.HostName = ""

	def __str__(self):
		return "[[ UserInfo - Channels: %s %s@%s on server %s ]]" % ( 
				self.Channels,
				self.Ident,
				self.HostName,
				self.Server )


def onLoad():
	@hook("join")
	def join_hook(ctx):
		global trackingData

		if ctx.isUs: # True if this is an event caused by us.
			trackingData[ctx.irc.network][ctx.chan] = ChannelInfo()
			ctx.irc.sendMessage("WHO", ctx.chan)


		networkData = trackingData[ctx.irc.network]

		if ctx.who.nick not in networkData[ctx.chan].Users:
			networkData[ctx.chan].Users.append(ctx.who.nick)

		if ctx.who.nick not in networkData:
			networkData[ctx.who.nick] = UserInfo()

		userData = networkData[ctx.who.nick]

		userData.Channels.append(ctx.chan)
		userData.HostName = ctx.who.host
		userData.Ident = ctx.who.ident

	@hook("part")
	def part_hook(ctx):
		global trackingData

		if ctx.isUs:
			del trackingData[ctx.irc.network][ctx.chan]
			return

		networkData = trackingData[ctx.irc.network]

		networkData[ctx.chan].Users.remove(ctx.who.nick)
		
		userData = networkData[ctx.who.nick]

		userData.Channels.remove(ctx.chan)
	
	@hook("nick")
	def nick_hook(ctx, new):
		global trackingData

		networkData = trackingData[ctx.irc.network]

		networkData[new] = networkData[ctx.who.nick]
		del networkData[ctx.who.nick]

		for chan in networkData[new].Channels:
			networkData[chan].Users.remove(ctx.who.nick)
			networkData[chan].Users.append(new)

	@hook("topic")
	def topic_hook(ctx, topic):
		global trackingData
		trackingData[ctx.irc.network][ctx.chan].Topic = topic

	@hook("irc_352")
	def irc_352_hook(ctx, msg):
		global trackingData

		ctx.chan = msg.args[1]
		whoNick = msg.args[5]

		networkData = trackingData[ctx.irc.network]

		if whoNick not in networkData:
			networkData[whoNick] = UserInfo()

		whoData = networkData[whoNick]
		chanData = networkData[ctx.chan]

		if ctx.chan not in whoData.Channels:
			whoData.Channels += [ ctx.chan ]

		if whoNick not in chanData.Users:
			chanData.Users.append(whoNick)

		whoData.HostName = msg.args[3]
		whoData.Server = msg.args[4]
		hops, realName  = msg.args[7].split(" ", 1)
		whoData.RealName = realName
		whoData.ServerHops = hops


	@hook("context_create")
	def context_create_hook(ctx):
		global trackingData

		if ctx.irc.network not in trackingData:
			return

		if ctx.who and ctx.who.nick in trackingData[ctx.irc.network]:
			ctx.userData = trackingData[ctx.irc.network][ctx.who.nick]
		else:
			ctx.userData = None

		if ctx.chan and ctx.chan in trackingData[ctx.irc.network]:
			ctx.chanData = trackingData[ctx.irc.network][ctx.chan]
		else:
			ctx.chanData = None

	@hook("connected")
	def connected_hook(irc):
		global trackingData

		trackingData[irc.network] = {}

	@injected
	def get_user_info(ctx, user):
		global trackingData

		return trackingData[ctx.irc.network][user]

	@injected
	def get_channel_info(ctx, chan):
		global trackingData

		return trackingData[ctx.irc.network][chan]
