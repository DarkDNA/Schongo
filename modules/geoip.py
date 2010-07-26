"""
Adds the 'geoip' command, which attempts to resolve a location for an IP or hostname.
"""

import urllib2

__info__ = {
	"Author": "Wil Hall",
	"Version": "1.0",
	"Dependencies": []
}

def onLoad():
	@command('geoip', 1)
	def geoip_cmd(ctx, cmd, arg, *args):
		ip = args[0]
		fornick = ''
		if '.' not in ip:
			ctx.reply(u'geoip by Nick not currently supported.', 'geoip')
			return
			fornick = u'for `B%s`B' % ip
			#host = m('chantrack').network(irc)[channel.lower()].users[ip.lower()].hostname
			host = host.split('@')
			ip = host[0]
		response = urllib2.urlopen('http://ipinfodb.com/ip_query2.php?ip=%s&timezone=false' % ip)
		geo = response.read()
		geo = geo.replace("""<?xml version="1.0" encoding="UTF-8"?>
<Locations>
  <Location id="0">
    <Ip>""", '')
		ip = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</Ip>
    <Status>""", '')
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</Status>
    <CountryCode>""", '')
		cc = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</CountryCode>
    <CountryName>""", '')
		country = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</CountryName>
    <RegionCode>""", '')
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</RegionCode>
    <RegionName>""", '')
		state = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</RegionName>
    <City>""", '')
		city = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</City>
    <ZipPostalCode>""", '')
		zip = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</ZipPostalCode>
    <Latitude>""", '')
		lat = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""</Latitude>
    <Longitude>""", '')
		lon = geo[0:geo.find('<')]
		geo = geo[geo.find('<'):]
		geo = geo.replace("""/Longitude>
  </Location>
</Locations>""", '')
		lon = lon.replace('\n', '').replace('\\n', '')
		ctx.reply(u"The IP Address `B%s`B %s traces to `B%s`B, `B%s`B, `B%s`B(`B%s`B) `B%s`B (`B%s`B, `B%s`B)." % (ip, fornick, city, state, country, cc, zip, lat, lon), 'geoip')
