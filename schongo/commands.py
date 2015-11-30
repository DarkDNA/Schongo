"""
Package commands handles the command parsing and dispatching to modules.
"""
from schongo.module_loader import hook, shutdown, fire_hook
from logging import getLogger

logger = getLogger("schongo.commands")

cfg_basic = None
commands = {}

def command(name, min=-1, max=-1):
    def retCmd(f):
        if (isinstance(name, list)):
            for n in name:
                commands[n.lower()] = f
        else:
            commands[name.lower()] = f

        f._min = min
        f._max = max
        return f

    return retCmd

def parent_cmd(name):
    ### TODO: Fix this so it assigns the proper __module__ value to the command - atm it will belong to __init__
    @command(name)
    def parentCmd(ctx, cmd, arg):
        if not handle_command(ctx, arg, cmd):
            ctx.error("No such sub-command")

def privs(level, *groups):
    def func(f):
        f._level = level
        f._groups = groups
        return f

    return func

def check_command(cmd, lvl, groups):
    if hasattr(cmd, "_level"):
        if cmd._level <= lvl:
            return True
        for g in cmd._groups:
            if g in groups:
                return True
        return False
    return lvl >= 1


def handle_command(ctx, line, parentcmd=None):
    parts = line.split(' ', 1)

    if ctx.who is not None:
        if hasattr(ctx.who, "level"):
            wholvl = ctx.who.level
        else:
            wholvl = 1

        if hasattr(ctx.who, "groups"):
            whogroups = ctx.who.groups
        else:
            whogroups = []

    cmd = parts[0]
    if parentcmd is not None:
        cmd = '%s %s' % (parentcmd, cmd)
    if len(parts) > 1:
        arg = parts[1]
        args = arg.split(' ')
    else:
        arg = ""
        args = []
    cmd = cmd.lower()
    if cmd in commands:
        cmdf = commands[cmd];
        # TODO: Implement Max args
        try:
            if not check_command(cmdf, wholvl, whogroups):
                ctx.error("You don't have permission to run that command")
            elif cmdf._min == -1:
                # Dumb command
                cmdf(ctx, cmd, arg);
            elif len(args) < cmdf._min:
                ctx.error("The command %s takes atleast %d arguments, %d given." % (cmd, cmdf._min, len(args)))
            else:
                cmdf(ctx, cmd, arg, *args)
        except Exception as e:
            logger.exception("Error running command %s", cmd)
        return True
    elif parentcmd is None:
        fire_hook("command", ctx, cmd, arg, args)
    else:
        return False

def init():
    logger.info("Initalising command system.")

    parent_cmd("load")
    parent_cmd("unload")

    @hook("module_unload")
    def module_unload(moduleInfo):
        toDel = []

        for cmd in commands:
            if commands[cmd].__module__ == moduleInfo.module:
                toDel.append(cmd)

        for cmd in toDel:
            del commands[cmd]

    @privs(5, "moduleadmin")
    @command(["load module", "load mod"], 1)
    def load_cmd(ctx, cmd, arg, *mods):
        """load module <mod1> [mod2]...
        Loads the given modules"""
        finalOutput = list()
        level = logging.WARN
        for mod in mods:
            if mod in ("-info", "-debug", "-warn", "-normal"):
                # If we are given a special directive (-info or -debug) we will load the remaining mods in
                # The list with a logging output level of the given value.
                if mod == "-info":
                    level = logging.INFO
                elif mod == "-debug":
                    level = logging.DEBUG
                elif mod == "-normal" or mod == "-warn":
                    level = logging.WARN
                continue;  # Skip the rest of the processing

            try:
                load_module(mod, MANUAL, level=level)
                finalOutput.append("`B%s`B: loaded" % mod)
            except Exception as e:
                finalOutput.append("`B%s`B: failed (%s)" % (mod, e))
                print_exc()
                unload_module(mod)

        if len(finalOutput) > 0:
            ctx.reply(', '.join(finalOutput), "Load")


    @privs(5, "moduleadmin")
    @command(["unload mod", "unload module"], 1)
    def unload_cmd(ctx, cmd, arg, *mods):
        """unload module <mod1> [mod2]...
    unloads the given modules additional commands may be added to this later, but for now module is the only one"""
        finalOutput = list()
        for mod in mods:
            try:
                unload_module(mod)
                finalOutput.append("`B%s`B: unloaded" % mod)
            except Exception as e:
                finalOutput.append("`B%s`B: failed (%s)" % (mod, e))

        if len(finalOutput) > 0:
            ctx.reply(', '.join(finalOutput), "Unload")


    parent_cmd("info")

    @command("info permissions", 0, 0)
    def info_perms_cmd(ctx, cmd, arg):
        if hasattr(ctx.who, "level"):
            ctx.reply("You are level %d and belong to the following groups: %s" % (
                ctx.who.level,
                ", ".join(ctx.who.groups)
            ))
        else:
            ctx.reply("There is no permission plugin loaded, please report this to the bot adminenstrator.")


    @command(["info module", "info mod"], 1, 1)
    def info_mod_cmd(ctx, cmd, arg, m, *args):
        """info module <module>
    Retrieves additional information about the module"""
        ctx.reply("Information available for module %s:" % m)
        try:
            mod = mods[m]

            ctx.reply("Author: %s" % mod.author, m)
            ctx.reply("Version: %s" % mod.version, m)
            if len(mod.deps):
                ctx.reply("Depends on: %s" % ', '.join([x.name for x in mod.deps]), m)
            if len(mod.depOf):
                ctx.reply("Depended on by: %s" % ', '.join([x.name for x in mod.depOf]), m)

            # ctx.reply("Desc: %s" % mod.desc, m)

        except KeyError:
            ctx.reply("[[ Information not available as module is not loaded. ]]")


    @command(["info command", "info cmd"])
    def info_cmd_cmd(ctx, cmd, arg):
        """info command <command>
    Spits out information for <command> (If we have any)"""
        if arg in commands:
            s = "Command %s" % arg
            theCmd = commands[arg]

            minarg = theCmd._min
            maxarg = theCmd._max

            if minarg != -1 and maxarg == -1:
                s += "(%d+)" % (minarg - 1)
            elif minarg == -1 and maxarg == -1:
                s += "(Any)"
            elif minarg == 0 and maxarg == 0:
                s += "(None)"
            elif minarg == maxarg:
                s += "(%d)" % minarg
            elif minarg != -1 and maxarg != -1:
                s += "(%d to %d)" % (minarg, maxarg)
            else:
                s += ": ** This should never happen **"

            if theCmd.__module__ != "modules":
                s += " from module %s: " % theCmd.__module__.split(".", 1)[1]
            else:
                s += ": "

            parts = (theCmd.__doc__ or "").split("\n", 1)
            usage = parts[0]

            if len(parts) > 1:
                body = parts[1]
            else:
                body = ""

            if usage != "":
                s += usage
            else:
                s += "[[ No usage info given. ]]"

            ctx.reply(s, "Info")

            if body != "":
                ctx.reply(body, "Info")
        else:
            ctx.reply("I don't seem to have any data available for that command.")


    @privs(5)
    @command("info networks", 0, 0)
    def info_networks_cmd(ctx, cmd, arg):
        """info networks
    Spits out information on the networks we are connected to."""
        s = "I am currently connected to the following networks: %s" % ', '.join(list(connections.keys()))
        ctx.reply(s, "Info")


    @privs(5)
    @command(["info modules", "info mods"], 0, 0)
    def info_modules_cmd(ctx, cmd, arg):
        """info modules
    Lists the currently loaded modules"""
        s = "I currently have the following modules loaded: %s" % ', '.join(list(mods.keys()))
        ctx.reply(s, "Info")


    @privs(5)
    @command("info threads", 0, 0)
    def info_threads_cmd(ctx, cmd, arg):
        """info threads
    Lists the currently running threads"""
        s = "I currently have the following threads running: %s"
        s = s % ', '.join([t.getName() for t in threading.enumerate()])
        ctx.reply(s, "Info")


    @privs(5)
    @command("shutdown")
    def shutdown_cmd(ctx, cmd, arg):
        """Shuts down the bot with the given message"""
        shutdown()
        # ctx.irc.disconnect(arg)
        if arg == "":
            arg = "Shutdown ordered by %s" % ctx.who.nick

        for net in connections:
            connections[net].disconnect(arg)

    @hook("irc_message")
    def command_processor(ctx, msg):
        if msg == "":
            return
        if msg[0] == cfg_basic.get("prefix char"):
            handle_command(ctx, msg[1:])
        elif msg.lower().startswith('%s: ' % ctx.irc.nick.lower()):
            handle_command(ctx, msg[len('%s: ' % ctx.irc.nick):]);
