"""
Provides a single command: wtf
This command looks up common acronyms.
"""

import glob
import re

splitter = re.compile("([A-Z]+)\s+(.+)")

def onLoad():
	acronyms = {}
	
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
						# DONGS DONGS DONGS

				acronyms[acronym] = meaning.strip()

	@command("wtf", 1, 1)
	def wtf_cmd(ctx, cmd, arg, word):
		word = word.upper()
		if word in acronyms:
			ctx.reply("%s: %s" % (word, acronyms[word]), "WTF")
		else:
			ctx.error("I don't know what %s means" % word)


