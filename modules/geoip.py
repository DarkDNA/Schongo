"""Adds the 'geoip' command, which attempts to resolve a location for an IP or hostname.

Config Note:
	Needs an entry in it's config file for an API key for ipinfodb.com
"""

import urllib2
import xml.dom.minidom as dom

__info__ = {
	"Author": "Wil Hall",
	"Version": "1.0",
	"Dependencies": []
}

def onLoad():
	@command('geoip', 1)
	def geoip_cmd(ctx, cmd, arg, ip, *args):
		if '.' not in ip:
			data = get_user_info(ctx, ip)
			if not data:
				ctx.error("Unknown user")
				return
			ip = data.HostName

		response = urllib2.urlopen('http://api.ipinfodb.com/v2/ip_query.php?key=%s&ip=%s&timezone=false' % (cfg.get("key"), ip))

		xml = dom.parse(response)

		def g(n, u="UNK"):
			d = xml.getElementsByTagName(n)[0].firstChild
			if d is not None:
				return d.data
			else:
				return u

		ip = g("Ip")
		cc = g("CountryCode")
		country = g("CountryName")
		region = g("RegionName")
		city = g("City")
		zip = g("ZipPostalCode")
		lat = g("Latitude")
		lon = g("Longitude")


		xml.unlink() # Phew! Release all the xml tree data now, since we just spent the code pulling it into vars. :)


		lon = lon.replace('\n', '').replace('\\n', '')
		ctx.reply(u"The IP Address %s traces to %s, %s, %s(%s) %s (%s, %s)." % (ip, city, region, country, cc, zip, lat, lon), 'geoip')
