"""
Provides a simple back-end for the privliages subsystem provided by the @privs decorator.
"""

from schongo.config import Config, NoSectionError
from schongo.module_loader import hook

permsconfig = Config()

def onLoad():
    permsconfig.read("data/simpleperms.cfg")

    @hook("context_create")
    def ctx_create(ctx):
        if ctx.who is None:
            return

        try:
            sect = permsconfig.get_section(ctx.who.nick)
        except NoSectionError:
            sect = None

        if sect is None:
            ctx.who.level = 1
            ctx.who.groups = []
        else:
            ctx.who.level = sect.getint("level")
            ctx.who.groups = sect.getlist("groups")
