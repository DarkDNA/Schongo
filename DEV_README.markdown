*** THIS README ASSUMES YOU KNOW PYTHON ON SOME LEVEL ***
It is not written to teach you python, just what we do with it for plugins.

= Intro =
	Selig has worked hard to make it so that plugins can be written for a large variety of things to do with minimal effort.
	In general, plugins should not need to  communicate with one-another, and is not easily possible at this time.
	*THIS IS BY DESIGN*
	It's designed with this feature omitted to prevent modules from requiring each other in ways that could cause a single module
	to become necessary to the core, which is against the design principals of the bot ( "Not too modular" ).



= Begining Notes =
	All hooks, commands, and timers must be defined in the onLoad function, or a function called from within the onLoad function.
	At this time, it is not possible to inject the command, timer, or hook function decorators into the module before it runs the top-level
	code.

	You will see things like 'ctx' in here; 'ctx' is the generic name for an IrcContext object

= IrcContext objects =
	You will notice we use the 'ctx' var a lot; it is referring to an IrcContext object.

	The IrcContext's main job is to simplify the reply to the given input, and to hold context information for an IRC Message, namely:
		* the calling irc client           ( irc )
		* The channel the event happen in  ( chan ) 
		* Who the event happen from        ( who )

	You shouldn't need to access these in general use, but they are available if needed.

	It's methods are below:
		reply(message,[tag, [parse, [parse newlines, [parse literal \n]]]])			
			Reply to the given context with the message of <message> - the given header tag of <tag>, and boolean values to turn on/off the parsing of newlines.

		error(message)
			Replys with an error result, with the error message of <message>.

		notice(message)
			Replys using a NOTICE message.

	There are more methods, but they are mostly for internal use.

	You can create an IrcContext with the method IrcContext.fromString(string[ , ctx]) - this parses a string of the form Network->#Channel
		* It also can parse just #channel if you pass a context to base it off of
	
	It *Is* Possible to make one from the constructor, but this is discuraged.


= Modules =
	Modules are just a collection of commands, hooks, and timers as well.
	They are meant to be self-sufficient.

	Modules can be documented using the docstring, which should be of the format "Short Description <newline> longer description".
	This is accessible to people via the 'info <module>' command.

= Adding commands =
	The Command decorator accepts from one to three arguments.
	@command(name[, minargs[, maxargs]])
	Only the first argument is required; if you do not give the min or max args, it assumes it is a "dumb" command, of the form :
	command(ctx, cmd, arg) Otherwise, it appends the given arguments using the python * operator. Thus, if you define a function with
	@command(name, 2) it must accept at least 2 arguments, or use the *args syntax to handle the arguments.
	
	Commands can be documented using the docstring of the function, and they should be of the form usage <newline> description.

	At this time there is no penalty for malformed commands, but in the future they may be removed from the command stack.


= Using Timers =
	When you use the timer decorator, I.e:
	@timer(time[, repeat])
	..you are specifying to the core that the below function is a timer for <time> seconds, and whether or not it should repeat.
	After this, the timer decorator adds two methods to the start function.
		start(*args, **kwargs)
			Starts the countdown. When it hits zero, it calls the timer with the given args and keyword args.
		cancel()
			Stops the countdown and resets the timer.
			Also stops the timer from repeating.
= Hooks =
	Hooks are a very complex subject, as they have no defined structure.
	They are defined with:
	@hook("hookName")
	and are of the form that the given hook must take
	The hook's and their forms are like so:
	
	-> message(ctx, message)
		Called on a message line received.

	-> action(ctx, msg)
		Called when somebody does a /me action in the channel.

	-> command(ctx, command, arg, args)
		Called when we detect a command. This is not recommended to be used for places where the @command decorator will work
		better, such as normal command usage, but instead for use of dynamic commands.

	-> join(ctx)
		Called when someone joins the channel.

	-> part(ctx, message)
		Called when someone parts the channel.

	-> quit(ctx, message)
		Called when someone quits from IRC.

	-> ctcp(ctx, cmd, arg)
		Called when we detect a CTCP message.
			* This is not called for the CTCP VERSION message

	-> module_preload(module name, module object)
		Called when a module has been loaded, but before the module's onLoad is called.

	-> module_load(module name, module object)
		Called after the module's onLoad has been called.

	-> module_unload(module name, module object)
		Called when we are unloading a module.
