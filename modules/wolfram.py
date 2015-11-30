"""
Querys Wolfram|Alpha and displays the results.

** Warning: Not all data is currently displayable **
"""

import urllib.request, urllib.error, urllib.parse
import xml.dom.minidom as dom

from schongo.commands import command

def Format_Pod(data):
    result = []

    for i in data.getElementsByTagName("subpod"):
        d = i.getElementsByTagName("plaintext")

        if not len(d):
            continue

        d = d[0]

        dat = ""

        if d.hasAttribute("title") and d.getAttribute("title") != "":
            dat = d.getAttribute("title") + ": "

        dat += d.firstChild.data

        dat = dat.replace("\n", " • ")

        result.append(dat)

    title = "Result"

    if data.hasAttribute("title") and data.getAttribute("title") != "":
        title = data.getAttribute("title")

    return "%s: %s" % (title, " / ".join(result))


def onLoad():
    @command("wolfram")
    def cmd_wolfram(ctx, cmd, arg):
        resp = urllib.request.urlopen("http://api.wolframalpha.com/v2/query?input=%s&format=plaintext&appid=%s" % (
        urllib.parse.quote(arg), cfg.get("key")))

        xml = dom.parse(resp)

        i = 0

        for pod in xml.getElementsByTagName("pod"):
            ctx.reply(Format_Pod(pod), "W|A", parse=False)
            i += 1

            if i > 3:
                ctx.reply("More can be obtained from the website.", "W|A")
                break

        if i == 0:
            ctx.reply("No valid response was received.", "W|A")
