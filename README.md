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

# choose #

Provides some random commands.


#### `@choose one or two or ... or n` ####
Picks from the given options - options are seperated by the string ' or '

#### `@8ball <life questions of great importance>` ####
Shakes the bot's built-in ( Free of charge! ) eight ball, and outputs the result

# debug_privs #
Provides a debug backend that grants everyone level 5 and admin.

# dynamic ( By Amanda Cameron ) #
Provides Dynamic commands to Schongo

Dynamic commands can use special syntax enhancements, such as %%Nick%% to refer to the person's nick, or %%Channel%% The syntax is as follows:

%%Variable%% - Replaced with the value of Variable
%[function name][function args]% - Dynamic function, such as random

== TODO ==
+ Implement the ability for other plugins to define functions and variables



#### `@add` ####
** No docstring given **

#### `@delete` ####
** No docstring given **

#### `@source` ####
** No docstring given **

#### `@say` ####
** No docstring given **

# market ( By Ross Delinger ) #

Working on an idea, if this works, authorized users should be able to install new modules!


#### `@register` ####
** No docstring given **

#### `@login` ####
** No docstring given **

#### `@authed` ####
** No docstring given **

# netcmds ( By Ross Delinger ) #

Module that wraps around ping and traceroute. 
The new and improved system uses a new threading technique to handle unix commands


#### `@ping <host>` ####
This command runs the ping command via the command line and outputs the results into irc

#### `@traceroute <host>` ####
Run traceroute or tracrt depending on system. Gets the route and timing to an IP address or domain name

# remote #

Provides remote-control functionality to Schongo


#### `@ping` ####
** No docstring given **

#### `@say` ####
** No docstring given **

# simple_privs #

Provides a simple back-end for the privliages subsystem provided by the @privs decorator.


# stackexchange ( By Ross Delinger ) #
 Interface with the Stack Exchange API Current only supports stackoverflow others may follow

#### `@so <netowkr> <tag1> <tag2> <etc>` ####
Search through the stackexchange network for the given tags

# test ( By Various ) #
Example Module to test various new features as they are added.

Feel free to add to them!


#### `@test timer start` ####
** No docstring given **

#### `@test timer stop` ####
** No docstring given **

#### `@test timer delay` ####
** No docstring given **

#### `@test crash` ####
** No docstring given **

#### `@test userinfo` ####
** No docstring given **

#### `@test chaninfo` ####
** No docstring given **

#### `@test say` ####
** No docstring given **

# unicode ( By Amanda Cameron ) #
Looks up information using the unicode database of happy! Yayyy!

#### `@unicode <char or search>` ####
Searches for information on the given char or, does an exact-match search for a char named in the args

# urllog ( By Amanda Cameron ) #
Sniffs URLs and shows the title for them, with special detection for sniffing youtube URLs

#### `@urllog` ####
** No docstring given **

# wikipedia #

Looks up information from a MediaWiki wiki - Currently only Wikipedia

Please note that this is still in development and needs some kinks to be worked out still


#### `@wikipedia <search>` ####
Searches through wikipedia for the given search string

# wolfram #

Querys Wolfram|Alpha and displays the results.

** Warning: Not all data is currently displayable **


#### `@wolfram` ####
** No docstring given **

# wtf #

Provides a single command: wtf
This command looks up common acronyms.


#### `@wtf` ####
** No docstring given **

#### `@port` ####
** No docstring given **

# youtube #
Implements various commands to interact with YouTube, and a meta information grabber

#### `@youtube <search string>` ####
Searches youtube for the given search string
