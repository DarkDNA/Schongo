"""Allows dns lookups by ip or by host"""
# coding=utf-8

import socket

def tryhostbyname(host):
	try:
		return socket.gethostbyname(host)
	except:
		return None

def tryhostbyaddr(ip):
	try:
		host, aliases, ip = socket.gethostbyaddr(ip)
		return host
	except:
		return None


def onLoad():
	@command("dns", 1, 1)
	def dns_cmd(ctx, cmd, arg, hostorip):
		"""dns <host|ip>
		Runs either a froward or backward lookup for host or ip"""
		host = tryhostbyaddr(hostorip)
		ip   = tryhostbyname(hostorip)

		if host is None and ip is None:
			ctx.error("Invalid host or IP Address")
			return

		if ip is None:
			ip = hostorip

		if host is None:
			host = hostorip

		ctx.reply(u"Host: %s • Ip: %s" % (host, ip), "DNS")

