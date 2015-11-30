"""
Working on an idea, if this works, authorized users should be able to install new modules!
"""
import hashlib
import time
import os

__info__ = {
    "Author": "Ross Delinger",
    "Version": "1.0",
    "Dependencies": []
}
users = dict()
authed = dict()


def registerUser(nick, password):
    global users
    password = hashlib.md5(password).digest()
    if not users.has_key(nick):
        # add a new user
        users[nick] = password


def authenticate(nick, password):
    global users
    global authed
    print
    nick
    print
    password
    password = hashlib.md5(password).digest()
    if users.has_key(nick):
        if users[nick] == password:
            authed[nick] = time.time()
            return True
    return False


def deauthenticate(nick):
    global authed
    if authed.has_key(nick):
        del authed[nick]
        return True
    return False


def isAuthenticated(nick):
    global authed
    if authed.has_key(nick):
        return True
    return False


def onLoad():
    @hook("module_load")
    def front_end_loader(ctx):
        # HAAAAXXXXXXX
        registerUser("Posiden", "12345")

    @command("register", 1, 1)
    def reg(ctx, cmd, arg, *args):
        if ctx.isPrivate and isAuthenticated(ctx.who.nick):
            result = registerUser(ctx.who.nick, arg)
            if result:
                ctx.reply("You have registered", "Market")
            else:
                ctx.reply("Registration failed", "Market")

    @command("login", 1, 1)
    def login(ctx, cmd, arg, *args):
        if ctx.isPrivate:
            result = authenticate(ctx.who.nick, arg)
            if result:
                ctx.reply("You Have successfully authenticated", "Market")
            else:
                ctx.reply("Authentication failed", "Market")

    @command("authed")
    def getAuthed(ctx, cmd, arg, *args):
        global authed
        le_authed = ' ,'.join([x for x in authed])
        ctx.reply("Authorized Users: %s" % le_authed, "Market")

    @timer(60, True)
    def cleaner():
        global authed
        if len(authed) > 0:
            currentTime = time.time()
            toDel = list()
            for user in authed:
                if (currentTime - authed[user]) >= 300:  # permissions time out after 5 min
                    toDel.append(user)

            for u in toDel:
                del authed[u]
        return True
