# encoding=utf8
"""Allows the bot to store quotes of people

Adds the following commands: remember, quote"""

from __future__ import with_statement
import pickle

global buffer

buffer = {}
quotes = []

__persist__ = ["quotes"]

def onLoad():	
	@command("quote", 1)
	def quote_cmd(ctx, cmd, arg, *args):
		qnum = -1
		try:
			qnum = int(arg) - 1
			try:
				quote = quotes[qnum]
			except KeyError:
				ctx.error("No such quote")
				return
		except:
			quote = ""
			for q in quotes:
				qnum += 1
				if arg in q:
					quote = q
					break

			if quote == "":
				ctx.error("Could not find any quote matching that string")
				return
				

		if qnum == -1:
			ctx.error("No such quote")
			return
		
		ctx.reply("Quote #%d:" % (qnum + 1), "Quote DB")
		ctx.reply(quote, "Quote DB")
	
				

	@command("remember", 2)
	def remember_cmd(ctx, cmd, arg, who, *args):
		global buffer
		what = ' '.join(args)

		# Multiple line quotes
		if "," in who:
			who = who.split(',')
		else:
			who = [who]

		# Start ... end quote
		p = what.split(' -to ', 2)
		start = p[0]
		if len(p) > 1:
			end = p[1]
		else:
			end = ""

		chanbuff = buffer["%s->%s" % (ctx.irc.network, ctx.chan)]

		quote = []

		record = False

		for w,type,line in chanbuff:
			if w in who:
				logger.debug("Processing line from %s: %s", w, line)

				if not record:
					if start in line:
						record = True
						logger.debug("Starting quote")
					else:
						logger.debug("Skipping line")
						continue

				fmt = "<%s> %s"

				if type == "action":
					fmt = "* %s %s"

				quote.append(fmt % (w, line))

				if end in line or end == "":
					logger.debug("Ending quote")
					break
		
		quotes.append('\n'.join(quote))
		ctx.reply("Remembered quote #%d" % len(quotes))

	@hook("action")
	def action_hook(ctx, msg):
		try:
			buf = buffer["%s->%s" % (ctx.irc.network, ctx.chan)]
		except:
			buf = []
	
		buf.append((ctx.who.nick, 'action', msg))

		buffer["%s->%s" % (ctx.irc.network, ctx.chan)] = buf
		
	
	@hook("message")
	def message_hook(ctx, msg):
		try:
			buf = buffer["%s->%s" % (ctx.irc.network, ctx.chan)]
		except:
			buf = []
	
		buf.append((ctx.who.nick, 'message', msg))

		buffer["%s->%s" % (ctx.irc.network, ctx.chan)] = buf
