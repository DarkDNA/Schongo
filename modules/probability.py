"""
Adds the 'probability' command, which calculates the number of possible word and sentence permutations, depending on word length.
"""

import urllib2
import urllib
import locale

locale.setlocale(locale.LC_ALL, '')

numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
nothing = ['']
lentoperm = {1:26, 2:650, 3:15600, 4:358800, 5:7893600, 6:165765600, 7:3315312000}

__info__ = {
    "Author": "Wil Hall",
    "Version": "1.0",
    "Dependencies": []
}

def onLoad():
    @command("probability", 1)
    def probability_cmd(ctx, cmd, arg, *args):
        if len(arg.split(' ')) != 0:
            if len(arg.split(' ')) == 1:
                arg0 = arg.split(' ')[0]
                if len(arg0) <= 7:
                    probability = lentoperm[len(arg0)]
                    probability = str(locale.currency(probability, grouping=True))
                    ctx.reply(u'\u0002[probability]\u0002 The probability of "%s" compared to all other possible words of its length is\u0002 %s\u0002 to \u00021\u0002 against.' % (arg0, probability[1:len(probability)-3]))
                else:
                    ctx.reply(u'\u0002[probability]\u0002 The probability of "%s" compared to all other possible words of its length is \u0002very unlikely\u0002 to \u00021\u0002 against.' % arg0)
            else:
                probability = 0
                veryunlikely = False
                for word in arg.split(' '):
                    #This is a sentence, so getting the probability of the /entire/ string would be incorrect. Instead we do (permutation of letters/numbers for length of word) * (permutation for arrangements of words in sentence) to get the total possible number of sentences that could result from arranging every possible word for each word's length.
                    if len(word) <= 7:
                        probability += lentoperm[len(word)] * len(args)
                    else:
                        veryunlikely = True
                if veryunlikely == False:
                    probability = str(locale.currency(probability, grouping=True))
                    ctx.reply(u'\u0002[probability]\u0002 The probability of this sentence, taking into account all the possible arrangements of all the possible words of all the given words\' lengths is\u0002 %s\u0002 to \u00021\u0002 against.' % probability[1:len(probability)-3])
                else:
                    ctx.reply(u'\u0002[probability]\u0002 The probability of this sentence, taking into account all the possible arrangements of all the possible words of all the given words\' lengths is \u0002very unlikely\u0002 to \u00021\u0002 against.')
        else:
            ctx.reply(u'\u0002[probability]\u0002 The probability of nothing, compared to every character you could have typed, assuming "nothing" is a character is\u0002 %s\u0002 to \u00021\u0002 against. Please provide input next time.' % (len(numbers) + len(letters) + len(nothing)))