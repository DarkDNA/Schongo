# coding=utf-8
"""
A weather forcast module that works using the weather underground api
"""
import urllib.request
import json

__info__ = {
	"Author": "Ross Delinger",
	"Version": "1.0",
	"Dependencies": []
}

weatherURL =  "http://api.wunderground.com/api/%s/conditions/q/%s.json"
forecastURL = "http://api.wunderground.com/api/%s/forcast/q/%s.json"

airportCache = {}

def onLoad():

	key = urllib.parse.quote(cfg.get("key"))
	
	@command("weather", 1)
	def weather(ctx, cmd, arg, *args):
		""" weather <location>
		Gives the weather for the given location, powered by Weather Underground.
		"""

		#xml = dom.parse(urllib.request.urlopen(weatherURL % (key, urllib.parse.quote(arg))))

		data = urllib.request.urlopen(weatherURL % (key, urllib.parse.quote(arg))).read().decode("utf8")
		data = json.loads(data)

		data = data["current_observation"]

		resp = "Current Conditions from %s" % data["observation_location"]["full"]

		resp += " • %s" % data["weather"]
		resp += " • Temperature: %s" % data["temperature_string"] #xml.getElementsByTagName("temperature_string")[0].firstChild.data
		resp += " • Winds: %s" % data["wind_string"] #xml.getElementsByTagName("wind_string")[0].firstChild.data

		ctx.reply(resp, "Weather")


	'''	
	@command("forecast", 1, 1)
	def forecast(ctx, cmd, arg, *args):
			"""weather <city>\nReturns the current forcast for the given area should be able to take area code or city"""
			url = forecastURL % (key, arg)
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
				'''
