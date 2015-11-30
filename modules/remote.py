"""
Provides remote-control functionality to Schongo
"""

from schongo.commands import command, privs

def onLoad():
    @command("ping")
    def ping_cmd(ctx, cmd, arg):
        ctx.reply("Pong!")

    @privs(2)
    @command("say")
    def say_cmd(ctx, cmd, arg):
        ctx.reply(arg)