# coding=utf-8
"""
A weather forcast module that works using the weather underground api
"""
import xml.dom.minidom as dom
import urllib2

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

weatherURL = 'http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?query=%s'
def onLoad():
	
	@command("weather", 1,1)
	def weather(ctx, cmd, arg, args):
			"""weather <city>\nReturns the current forcast for the given area should be able to take area code or city"""
			url = weatherURL % arg
			page = urllib2.urlopen(url)
			xml = dom.parse(page)
			titles = xml.getElementsByTagName('title')
			forcasts = xml.getElementsByTagName('fcttext')
			count = 0
			wDict = {}
			for t in titles:
				wDict[t.firstChild.data] = forcasts[count].firstChild.data
				count += 1
			
			for title in wDict:
				ctx.reply("%s: %s" % (title, wDict[title]), "Weather")