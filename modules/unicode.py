# coding=utf-8
"""Looks up information using the unicode database of happy! Yayyy!"""

import unicodedata

__info__ = {
	"Author": "Amanda Cameron",
	"Version": "0.1a",
	"Dependencies": ""
}

abbrTable = {
	"Lu": "Uppercase Letter",
	"Ll": "Lowercase Letter",
	"Lt": "Titlecase Letter",
	"Lo": "Other Letter",
	"Mn": "Nonspacing Mark",
	"Mc": "Spacing Mark",
	"Me": "Enclosing Mark",
	"Nd": "Decimal Number",
	"Nl": "Letter Number",
	"No": "Other Number",
	"Pc": "Connector Puncuation",
	"Pd": "Dash Puncuation",
	"Ps": "Open Puncuation",
	"Pe": "Close Puncuation",
	"Pi": "Initial Puncuation",
	"Pf": "Final Puncuation",
	"Po": "Other Puncuation",
	"Sm": "Math Symbol",
	"Sc": "Currency Symbol",
	"Sk": "Modifier Symbol",
	"So": "Other Symbol",
	"Zs": "Space Seperator",
	"Zl": "Line Seperator",
	"Zp": "Paragraph Seperator",
	"Cc": "Control Char",
	"Cf": "Format Char",
	"Cs": "Surrogate Char",
	"Co": "Private Use Char",
	"Cn": "Unassigned"
}

def onLoad():
	@command("unicode", 1, 1)
	def unicode_cmd(ctx, cmd, arg, charOrSearch, *args):
		"""unicode <char or search>
Searches for information on the given char or, does an exact-match search for a char named in the args"""
		if len(charOrSearch) == 1:
			# Likly a search-by-glyph
			char = charOrSearch[0]
		else:
			try:
				char = unicodedata.lookup(arg)
			except:
				ctx.error("Unknown char name %s" % arg)
				return

		name = unicodedata.name(char, "Unknown Unicode Char").title()
		cat = unicodedata.category(char)
		num = ord(char)
		
		if cat in abbrTable:
			cat = abbrTable[cat]
		else:
			cat = "Unknown Category(%s)" % cat

		ctx.reply("Char %s • U+%04X • %s • %s" % (char, num, name, cat), "Unicode")
			
