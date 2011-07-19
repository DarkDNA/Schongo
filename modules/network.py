"""Allows dns lookups by ip or by host"""
# coding=utf-8

import socket

def trygetaddrinfo(host):
	try:
		data = {}
		data["ipv4"] = {}
		data["ipv6"] = {}
		for family, socktype, proto, cannonname, sockaddr in socket.getaddrinfo(host, None):
			if family == socket.AF_INET:
				ip, port = sockaddr
				data["ipv4"][ip] = None #.append(ip)
			elif family == socket.AF_INET6:
				ip, port, flow, info = sockaddr
				data["ipv6"][ip] = None #.append(ip)
			else:
				logger.warn("Unknown family for this query type: %d", family)

		data["ipv4"] = data["ipv4"].keys()
		data["ipv6"] = data["ipv6"].keys()

		return data
	except socket.gaierror:
		return None
		pass


def tryhostbyaddr(ip):
	try:
		host, aliases, ip = socket.gethostbyaddr(ip)
		return host
	except:
		return None


def onLoad():

	def maybes(li):
		if len(li) > 1:
			return "s", ", ".join(li)
		else:
			return "", ", ".join(li)

	@command("dns", 1, 1)
	def dns_cmd(ctx, cmd, arg, hostorip):
		"""dns <host|ip>
		Runs either a froward or backward lookup for host or ip"""
		host = tryhostbyaddr(hostorip)
		ips  = trygetaddrinfo(hostorip)

		if host is None and ips is None:
			ctx.error("Invalid host or IP Address")
			return

		

		if host is None:
			host = hostorip

		s = u"Host: %s" % host

		if len(ips["ipv4"]) or len(ips["ipv6"]):
			if len(ips["ipv4"]):
				s += u" • Ip%s: %s" % maybes(ips["ipv4"])

			if len(ips["ipv6"]):
				s += u" • Ip%s (v6): %s" % maybes(ips["ipv6"])
		else:
			s += u" • Unknown Ip"

		ctx.reply(s, "DNS");
		#ctx.reply(u"Host: %s • Ip: %s" % (host, ip), "DNS")

