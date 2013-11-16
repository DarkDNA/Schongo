# Schongo Modular Bot #
Schongo is an IRC bot designed to be as modular as possible, with no single module being required for core functionality (Such as talking to the IRC Server itself) -- Note that at this time it is not completely meeting this goal (_tracking is hard-loaded by the core, and can not handle being unloaded), However Amanda is working hard to make this happen.

Schongo is being written by:

- Amanda Cameron
- Ross Delinger (Posiden)
- Wil Hall

# Plans for the future #
Please read the TODO file.

# Setup #
To setup Schongo: copy data/example.cfg to data/config.cfg
Then edit config.cfg with the irc network details

Then type this into terminal or cmdline:  
> python schongo.py

# Development #
Please take a look at the DEV\_README.md for information on development for the Schongo IRC Bot

# Basics #

## Commands ##
By default, Schongo uses the char '@' for commands, so that is the char that this document will use to describe commands
Commands are of the form
`@command arg1 arg2 ... argn` 
some commands may have sub-commands which take the form of 
`@command subcommand arg1 arg2 ... argn`

## Modules ##
You can load and unload modules at runtime with the commands
`@load module module module module` and `@unload module module module module`
