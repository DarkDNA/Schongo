# coding=utf-8
"""
A weather forcast module that works using the weather underground api
"""
import xml.dom.minidom as dom
import urllib.request

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

forecastURL = 'http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?query=%s'
lookupURL = 'http://api.wunderground.com/auto/wui/geo/GeoLookupXML/index.xml?query=%s'
weatherURL = 'http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query=%s'

airportCache = {}

def onLoad():
	
	@command("weather", 1)
	def weather(ctx, cmd, arg, *args):
		""" weather <location>
		Gives the weather for the given location, powered by Weather Underground.
		"""
		# TODO: Better caching -- also, personal weather stations should be included and the closest to the input given selected

		if arg in airportCache:
			airport = airportCache[arg]
		else:
			xml = dom.parse(urllib.request.urlopen(lookupURL % arg))
			airport = xml.getElementsByTagName("station")[0].getElementsByTagName("icao")[0].firstChild.data

			airportCache[arg] = airport

		xml = dom.parse(urllib.request.urlopen(weatherURL % airport))

		resp = "Current Conditions from %s" % xml.getElementsByTagName("observation_location")[0].getElementsByTagName("full")[0].firstChild.data

		resp += " • %s" % xml.getElementsByTagName("weather")[0].firstChild.data
		resp += " • Temperature: %s" % xml.getElementsByTagName("temperature_string")[0].firstChild.data
		resp += " • Winds: %s" % xml.getElementsByTagName("wind_string")[0].firstChild.data

		ctx.reply(resp, "Weather")


	@command("forecast", 1, 1)
	def forecast(ctx, cmd, arg, *args):
			"""weather <city>\nReturns the current forcast for the given area should be able to take area code or city"""
			url = forecastURL % arg
			page = urllib.request.urlopen(url)
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
