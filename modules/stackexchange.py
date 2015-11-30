# coding=utf-8
""" Interface with the Stack Exchange API Current only supports stackoverflow others may follow"""

import gzip
import json
from urllib import request

from schongo.utils import prettyNumber
from schongo.commands import command

__info__ = {
    "Author": "Ross Delinger",
    "Version": "1.1.0",
    "Dependencies": []
}

baseURL = "http://{}.{}.com{}"
apiURLS = {"so": baseURL.format('api', 'stackoverflow', '/1.0/{}'),
           "su": baseURL.format('api', 'superuser', '/1.0/{}'),
           "sf": baseURL.format('api', 'serverfault', '/1.0/{}')
           }

questionURLS = {"so": baseURL.format('www', 'stackoverflow', '/{}/{}'),
                "su": baseURL.format('www', 'superuser', '/{}/{}'),
                "sf": baseURL.format('www', 'serverfault', '/{}/{}')
                }
expandedNames = {"so": "StackOverflow",
                 "su": "SuperUser",
                 "sf": "ServerFault"
                 }


def jsonLoad(string):
    string = str(string.decode('utf-8'))
    string = string.replace("\r\n", "")
    return json.loads(string)


def onLoad():
    @command("stackexchange", 2)
    def search(ctx, cmd, arg, *args):
        """so <netowkr> <tag1> <tag2> <etc>\nSearch through the stackexchange network for the given tags"""
        network = args[0]
        args = args[1:]

        thingy = ";".join(args)
        searchQuery = 'search?tagged={}&pagesize=3'.format(thingy)
        if network in apiURLS:
            apiURL = apiURLS[network]
        else:
            ctx.reply("Invalid Network", "StackExchange")
            return
        searchURL = apiURL.format(searchQuery)
        data = request.urlopen(searchURL).read()
        jsonData = gzip.decompress(data)
        decoded = jsonLoad(jsonData)
        results = decoded["total"]
        if results > 0:
            res = min(results, 3)
            ctx.reply("Results 1-{} of {}".format(res, prettyNumber(results)), expandedNames[network])
        else:
            ctx.reply("No results for your query", expandedNames[network])
        for q in decoded['questions']:
            title = q['title']
            questionURL = questionURLS[network].format('questions', q['question_id'])
            ctx.reply('{} • {}'.format(title, questionURL), expandedNames[network])
