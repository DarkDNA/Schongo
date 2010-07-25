"""
Adds the 'bitly' command, which takes 1 URL as an argument. If the URL is not a bitly URL, it returns a bitly URL linked to the given URL. If the URL given is a bitly URL, it returns the real URL which the given bitly URL links to.
"""

import urllib2
import urllib

__info__ = {
    "Author": "Wil Hall",
    "Version": "1.0",
    "Dependencies": []
}

def onLoad():
    @command('bitly', 1)
    def bitly_cmd(ctx, cmd, arg, *args):
        args = arg.split(' ')
        if len(args) > 0:
            if 'http://bit.ly/' in args[0]:
                try:
                    request = urllib2.Request(args[0])
                    opener = urllib2.build_opener()
                    response = opener.open(request)
                    url = response.url
                    ctx.reply(u"`BActual URL:`B %s" % url, 'bitly')
                except URLError:
                    ctx.reply(u"`BError:`B Unable to open URL `B%s`B." % args[0], 'bitly')
            else:
                response = urllib2.urlopen("http://api.bit.ly/v3/shorten?login=wilatkathbot3&apiKey=R_8fa4afa5dda9ae6cab93896eaf04c8de&longUrl=%s&format=txt" % urllib.quote(args[0], ':/').strip().rstrip())
                url = response.read()
                ctx.reply(u"`Bbit.ly URL:`B %s" % url, 'bitly')