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
	handle = open('data/cypherdata.pickle', 'wb+')
	pickle.dump(charsets, handle)
	handle.close()

def load():
	global charsets
	try:
		handle = open('data/cypherdata.pickle', 'rb')
		charsets = pickle.load(handle)
		handle.close()
		if len(charsets) == 0:
			charsets = {
				'abc':list('abcdefghijklmnopqrstuvwxyz'),
				'cba':list('zyxwvutsrqponmlkjihgfedcba')
				}
	except IOError:
		if len(charsets) == 0:
			charsets = {
				'abc':list('abcdefghijklmnopqrstuvwxyz'),
				'cba':list('zyxwvutsrqponmlkjihgfedcba')
				}
		save()

def onLoad():
	load()
	parent_cmd('cypher')
	
	@command('cypher addcharset', 2)
	def addcharset_cmd(ctx, cmd, arg, charset, values, *args):
		"""cypher addcharset <setname> <set>
Add a character set for future use. <set> should be like abcdefghijklmnopqrstuvwxyz Where each character will be interpreted respectively."""
		global charsets
		if charset not in charsets:
			charsets[charset] = list(values)
			ctx.reply('Added character set `B"%s"`B.' % charset, 'cyphertools')
			save()
		else:
			ctx.reply('A character set with the name `B"%s"`B already exists.' % charset, 'cyphertools')
	
	@command('cypher view', 1)
	def view_cmd(ctx, cmd, arg, charset, *args):
		"""cypher view <setname>
View a character set"""
		if charset in charsets:
			ctx.reply('`B%s:`B %s' % (charset, listify(charsets[charset])), 'cyphertools')
		else:
			ctx.reply('No character set with the name `B"%s"`B exists.' % charset, 'cyphertools')
	
	@command('cypher delcharset', 1)
	def delcharset_cmd(ctx, cmd, arg, charset, *args):
		"""cypher delcharset <set>
Deletes the given char set"""
		global charsets
		if charset in charsets:
			del charsets[charset]
			ctx.reply('Removed character set `B"%s"`B.' % charset, 'cyphertools')
			save()
		else:
			ctx.reply('No character set with the name `B"%s"`B exists.' % charset, 'cyphertools')
	
	@command('cypher replace', 3)
	def replace_cmd(ctx, cmd, arg, fromset, toset, *args):
		"""cypher replace <from> <to> <text>
Replacement cypher"""
		
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
	
	@command('cypher shift', 2)
	def shift_cmd(ctx, cmd, arg, charset, num, *args):
		"""cypher shift <set> <num> <text>
Shift Cypher"""

		if charset not in charsets:
			ctx.reply('No character set with the name `B"%s"`B exists.' % charset, 'cyphertools')
			return
		charset = charsets[charset]
		
		num = int(num)

		text = ' '.join(args)
		ntext = ''
		for char in text:
			char = char.lower()
			if char in charset:
				index = charset.index(char) + num
				if index > len(charset)-1:
					index -= len(charset)-1
				elif index < 0:
					index = len(charset)-((index*-1)-1)
				ntext += charset[index]
			else:
				ntext += char
		ctx.reply('`BResult:`B %s' % ntext, 'cyphertools')

def onUnload():
	save()
