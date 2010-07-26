"""
Adds the 'translationparty' command, allowing users to connect to google translator to translate a phrase back and forth from English to Japanese, using translationparty.com's phrases after an equilibrium is found.
"""

import json
import urllib2
import random

# Various UAs from Safari's Develop menu.
USER_AGENTS = (
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_7; en-us) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Safari/530.17',
    'Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.10) Gecko/2009042315 Firefox/3.0.10',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10',
    'Opera/9.64 (Macintosh; Intel Mac OS X; U; en) Presto/2.1.1',
    'Opera/9.64 (Windows NT 6.0; U; en) Presto/2.1.1',
)

def load_url(url):
    handle = urllib2.urlopen(urllib2.Request(url, headers={'User-Agent': random.choice(USER_AGENTS), 'Referrer': 'http://darkdna.net/'}))
    data = handle.read().decode('utf-8')
    handle.close()
    return data

def escapeurl(url):
    safe = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
    output = ''
    for char in url:
        if char in safe:
            output += char
        else:
            code = hex(ord(char))[2:]
            while len(code) > 0:
                if len(code) == 1:
                    code = '0' + code
                output += '%' + code[0:2]
                code = code[2:]
    return output

successstrings = {
'uppercase': ["But it's not nice to shout in Japanese, either."],
'lowercase': ["But would it kill you to capitalize properly?"],
'dirty': ["Shame on you, by the way.",
            "With language like that, you're a real goodwill ambassador!"],
'twitter': ["This is better than Twitter, admit it."],
'meme': ["You're sure are up on your Internet jokes!",
            "That Internet joke is funny in any language!"],
'tp': ["Translation Party was made by Will Carlough and Richard Boenigk. <br />Send us an email at <a href='mailto:translationparty@gmail.com'>translationparty@gmail.com</a>"],
'darkdna': ["So, you like DarkDNA?",
			"Don't forget to visit us at irc.darkdna.net/#lobby.",
			"Schongo originated on DarkDNA, you know."],
'multipurpose': ["This is a real translation party!",
				    "You should move to Japan!",
				    "You've done this before, haven't you.",
				    "Okay, I get it, you like Translation Party.",
				    "That's deep, man.",
				    "Come on, you can do better than that.",
				    "That didn't even make that much sense in English.",
                    "You've heard about <a href='http://questionparty.com'>Question Party</a> right?",
				    "Translation Party is hiring, you know."],
}

def successstring(eq):
    if eq.lower() == eq:
        return successstrings['lowercase'][random.randint(0,len(successstrings['lowercase'])-1)]
    elif eq.upper() == eq:
        return successstrings['uppercase'][random.randint(0,len(successstrings['uppercase'])-1)]
        
    profanities = ['fuck', 'shit', 'ass', 'tit', 'bitch', 'screw', 'dick', 'pussy', 'nuts', 'balls']
    for profanity in profanities:
        if profanity in eq:
            return successstrings['dirty'][random.randint(0,len(successstrings['dirty'])-1)]
    
    memes = ['i can has', 'i can haz', 'all your base', 'never gonna']
    for meme in memes:
        if meme in eq:
            return successstrings['meme'][random.randint(0,len(successstrings['meme'])-1)]
    
    if 'twitter' in eq or 'tweet' in eq:
        return successstrings['tp'][random.randint(0,len(successstrings['tp'])-1)]
    
    tp = ['translation', 'party', 'who made', 'who built', 'will', 'carlough', 'rick', 'richard', 'boenigk']
    for t in tp:
        if t in eq:
            return successstrings['tp'][random.randint(0,len(successstrings['tp'])-1)]
    
    if 'darkdna' in eq.lower():
    	return successstrings['darkdna'][random.randint(0,len(successstrings['meme'])-1)]
    
    return successstrings['multipurpose'][random.randint(0,len(successstrings['multipurpose'])-1)]

    
        

def onLoad():
    @command('translationparty', 1)
    def translationparty_cmd(ctx, cmd, arg, *args):
        args = arg.split(' ')
        message = ' '.join(args)
        lengres = 'null'
        lres = 'null'
        res = message
        lang = 'en'
        ctx.reply(u"`BLet's Go!:`B %s" % message, 'translationparty')
        while lengres != res:
            if lang == 'en':
                data = load_url("http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=" + escapeurl(res.encode('utf-8')) + "&langpair=en%7Cja")
                parsed = json.loads(data)
                response = parsed['responseData']['translatedText']
                if lengres == 'null':
                    ctx.reply(u"`BInto Japanese:`B %s" % response, 'translationparty')
                else:
                    ctx.reply(u"`BBack into Japanese:`B %s" % response, 'translationparty')
                lengres = res
                lres = res
                res = response
                lang = 'ja'
            else:
                data = load_url("http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=" + escapeurl(res.encode('utf-8')) + "&langpair=ja%7Cen")
                parsed = json.loads(data)
                response = parsed['responseData']['translatedText']
                ctx.reply(u"`BBack into english:`B %s" % response, 'translationparty')
                lres = res
                res = response
                
                lang = 'en'
        ctx.reply(u"`BEquilibrium found! %s`B" % successstring(lengres), 'translationparty')
        
                

    