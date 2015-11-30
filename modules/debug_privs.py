"""Provides a debug backend that grants everyone level 5 and admin."""
from schongo.module_loader import hook

def onLoad():
    @hook("context_create")
    def ctx_config(ctx):
        if ctx.who is None:
            return

        ctx.who.level = 5
        ctx.who.groups = ["admin", "debug"]