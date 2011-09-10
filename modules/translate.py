"""Translation module for Schongo."""

import urllib.request, urllib.parse
import re
import json
from modules._utils import unescapeHtml

def translate(what, src=None, target="en"):
	url = "https://www.googleapis.com/language/translate/v2?key=%s&target=%s" % (urllib.parse.quote(cfg.get("key")), target);
	if src is not None:
		url += "&source=" + urllib.parse.quote(src);
	url += "&q=" + urllib.parse.quote(what)

	f = urllib.request.urlopen(url);
	data = json.loads(f.read().decode("utf-8"))

	if "detectedSourceLanguage" in data["data"]["translations"][0]:
		return data["data"]["translations"][0]["detectedSourceLanguage"], data["data"]["translations"][0]["translatedText"]
	elif src is not None:
		return src, unescapeHtml(
				data["data"]["translations"][0]["translatedText"])
	else:
		return "unk", unescapeHtml(
				data["data"]["translations"][0]["translatedText"])

def onLoad():

	languages = []

	url = "https://www.googleapis.com/language/translate/v2/languages?key=%s" % urllib.parse.quote(cfg.get("key"))

	f = urllib.request.urlopen(url)
	data = json.loads(f.read().decode("utf-8"))

	for i in data["data"]["languages"]:
		languages.append(i["language"])

	@command("translate", 1)
	def translate_cmd(ctx, cmd, arg, *unused):
		"""translate (src=>target) something here
Translates from src to target ( auto-detect and english if unspecified ) and spits out the result.
Uses Google Translate."""
		src=None
		targ="en"

		m = re.match("([^ =]+)=>([^ ]+)", arg)
		if m is not None:
			src=m.group(1)
			targ=m.group(2)

			if src not in languages or targ not in languages:
				ctx.error("Invalid Language")
				return

			arg = arg[arg.find(" ")+1:]


		lang, trans = translate(arg, src, targ)
		ctx.reply(trans, "%s=>%s" % (lang, targ))
