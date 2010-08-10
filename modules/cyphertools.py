"""Adds the cypher command for applying various cyphers to text."""

import os
import pickle
from _utils import listify

__info__ = {
    "Author": "Wil Hall",
    "Version": "1.0",
    "Dependencies": []
}

charsets = {}

def save():
    global charsets
    handle = open(os.getcwd() + '\data\cypherdata.pickle', 'w+')
    pickle.dump(charsets, handle)
    handle.close()

def load():
    global charsets
    try:
        handle = open(os.getcwd() + '\data\cypherdata.pickle', 'r')
        charsets = pickle.load(handle)
        handle.close()
        if len(charsets) == 0:
            charsets = {'abc':list('abcdefghijklmnopqrstuvwxyz'), 'cba':list('zyxwvutsrqponmlkjihgfedcba')}
    except IOError:
        if len(charsets) == 0:
            charsets = {'abc':list('abcdefghijklmnopqrstuvwxyz'), 'cba':list('zyxwvutsrqponmlkjihgfedcba')}
        save()

def onLoad():
    load()
    # cypher <type> <type-specific arguments> <text>
    parent_cmd('cypher')
    
    #Add a character set for future use. <set> should be like abcdefghijklmnopqrstuvwxyz Where each character will be interpreted respectively.
    # cypher addcharset <setname> <set>
    @command('cypher addcharset', 2)
    def addcharset_cmd(ctx, cmd, arg, *args):
        global charsets
        if args[0] not in charsets:
            charsets[args[0]] = list(args[1])
            ctx.reply('Added character set `B"%s"`B.' % args[0], 'cyphertools')
            save()
        else:
            ctx.reply('A character set with the name `B"%s"`B already exists.' % args[0], 'cyphertools')
    
    #View a character set.
    # cypher view <setname>
    @command('cypher view', 1)
    def view_cmd(ctx, cmd, arg, *args):
        if args[0] in charsets:
            ctx.reply('`B%s:`B %s' % (args[0], listify(charsets[args[0]])), 'cyphertools')
        else:
            ctx.reply('No character set with the name `B"%s"`B exists.' % args[0], 'cyphertools')
    
    #Add a character set for future use. <set> should be like abcdefghijklmnopqrstuvwxyz Where each character will be interpreted respectively.
    # cypher delcharset <setname>
    @command('cypher delcharset', 1)
    def delcharset_cmd(ctx, cmd, arg, *args):
        global charsets
        if args[0] in charsets:
            del charsets[args[0]]
            ctx.reply('Removed character set `B"%s"`B.' % args[0], 'cyphertools')
            save()
        else:
            ctx.reply('No character set with the name `B"%s"`B exists.' % args[0], 'cyphertools')
    
    #Replacement Cyper
    # cypher replace <from-char-set> <to-char-set> <text>
    @command('cypher replace', 3)
    def replace_cmd(ctx, cmd, arg, *args):
        args = arg.split(' ')
        fromset = args.pop(0)
        toset = args.pop(0)
        
        if fromset not in charsets:
            ctx.reply('No character set with the name `B"%s"`B exists.' % fromset, 'cyphertools')
            return
        if toset not in charsets:
            ctx.reply('No character set with the name `B"%s"`B exists.' % toset, 'cyphertools')
            return
        
        fromset = charsets[fromset]
        toset = charsets[toset]

        text = ' '.join(args)
        ntext = ''
        if len(fromset) != len(toset):
            ctx.reply('These character sets cannot be used together because they are not of the same length.', 'cyphertools')
            return
        
        for char in text:
            char = char.lower()
            if char in fromset:
                ntext += toset[fromset.index(char)]
            else:
                ntext += char
        ctx.reply('`BResult:`B %s' % ntext, 'cyphertools')
    
    #Shift Cyper
    # cypher shift <set> <num> <text>
    @command('cypher shift', 2)
    def shift_cmd(ctx, cmd, arg, *args):
        args = arg.split(' ')
        
        set = args.pop(0)
        if set not in charsets:
            ctx.reply('No character set with the name `B"%s"`B exists.' % set, 'cyphertools')
            return
        set = charsets[set]
        
        num = int(args.pop(0))
        text = ' '.join(args)
        ntext = ''
        for char in text:
            char = char.lower()
            if char in set:
                index = set.index(char) + num
                if index > len(set)-1:
                    index -= len(set)-1
                elif index < 0:
                    index = len(set)-((index*-1)-1)
                ntext += set[index]
            else:
                ntext += char
        ctx.reply('`BResult:`B %s' % ntext, 'cyphertools')
        
    
