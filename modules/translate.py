"""Translation module for Schongo."""

import urllib
import re
import json
from _utils import unescapeHtml

def jsonLoad(fp):
	if hasattr(json, "load"):
		# Proper json module 2.6+
		return json.load(fp)
	elif hasattr(json, "read"):
		# python-support hack
		return json.read(fp.read())
	else:
		return {
		"data": { "translations": {
			"tranlatedText": "JSON Error, please contact bot admininstrator."
		}}};

def translate(what, src=None, target="en"):
	url = "https://www.googleapis.com/language/translate/v2?key=%s&target=%s" % (urllib.quote(cfg.get("key")), target);
	if src is not None:
		url += "&source=" + urllib.quote(src);
	url += "&q=" + urllib.quote(what.encode("utf-8"))

	f = urllib.urlopen(url);
	data = jsonLoad(f);

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

	url = "https://www.googleapis.com/language/translate/v2/languages?key=%s" % urllib.quote(cfg.get("key"))
	f = urllib.urlopen(url)
	data = jsonLoad(f)

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
