"""
Provides a single command: wtf
This command looks up common acronyms.
"""

import glob
import re

splitter = re.compile("(.+)\t([0-9])/(sctp|tcp|udp)\t([0-9]\.[0-9]+).+(#.+)?")

def onLoad():
	acronyms = {}
	ports = {}

	for db in glob.glob("/usr/share/misc/acronyms*"):
		with open(db, "r") as f:
			for line in f:
				line = line.strip()
				try:
					acronym, meaning = line.split("\t", 1)
				except ValueError:
					try:
						acronym, meaning = line.split(" ", 1)
					except ValueError:
						pass
				acronyms[acronym] = meaning.strip()
	
	n = 0
	try:
		with open("/usr/share/nmap/nmap-services", "r") as f:
			for line in f:
				line = line.strip()
				if line[0] == "#":
					continue
				"""g = splitter.match(line)
				if g is None:
					n += 1
					if n < 5:
						logger.error("Invalid line: %s", line)
					continue
				name = g.group(1)
				port = int(g.group(2))
				which = g.group(3)
				comment = g.group(5)"""

				try:
					line, comment = line.split("#")
				except:
					comment = "No comment"

				name, portproto, _ = line.split("\t", 2)

				port, proto = portproto.split("/")

				port = int(port)

				if proto not in ports:
					ports[proto] = {}

				ports[proto][port] = (name, comment)

		for proto in ports:
			logger.info("Found %d ports for %s", len(ports[proto]), proto)

	except IOError:
		logger.error("the port command will not be supported because we could not find the nmap service database")
	

	
	@command("wtf", 1, 1)
	def wtf_cmd(ctx, cmd, arg, word):
		word = word.upper()
		if word in acronyms:
			ctx.reply("%s: %s" % (word, acronyms[word]), "WTF")
		else:
			ctx.error("I don't know what %s means" % word)
	
	if len(ports) != 0:
		@command("port", 1, 1)
		def port_cmd(ctx, cmd, arg, port):
			port = int(port)
			for proto in ports:
				if port in ports[proto]:
					ctx.reply("%s: %s" % ports[proto][port], proto)
