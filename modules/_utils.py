import locale

locale.setlocale(locale.LC_ALL, "")

def prettyNumber(num):
	return locale.format("%d", int(num), 1)

def prettyTime(secs):
	if not isinstance(secs, int):
		secs = int(secs)
	mins = secs // 60
	hours = mins // 60 # There are actualy some hour+ long youtube videos

	secs = secs % 60
	mins = mins % 60

	time = "%02d:%02d" % (mins, secs)

	if hours > 0:
		time = "%d:%s" % (hours, time)

	return time
