#!/usr/bin/env python

import sys
import os.path

from glob import glob
from traceback import print_exc

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Functions to simulate the environment

def command_decorator(command, minarg=-1, maxarg=-1, *args, **kwargs):
    if isinstance(command, list):
        command = '|'.join(command)

    def func(func):
        synapsis = command
        body = ""
        output("")
        if func.__doc__ is not None:
            # It's a good function and defines a doc string
            func.__doc__.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            parts = func.__doc__.split("\n", 1)
            synapsis = parts[0]

            if len(parts) > 1:
                body = parts[1]
            else:
                body = "** No description given **"
                print("** WARN - command %s has no docs" % command)
        else:
            print("** WARN - command %s has no docstring" % command)
            body = "** No docstring given **"

        output("#### `@%s` ####", synapsis)
        output(body)
        return func

    return func


def hook_decorator(hook):
    def func(func):
        return func

    return func

def noFunc(*a, **kw):
    pass

def timer_decorator(time, singleton=False):
    def func(func):
        func.start = noFunc
        func.cancel = noFunc
        func.delay = noFunc
        func.reset = noFunc
        return func

    return func


# Output the given string to the file

def output(fmt, *args):
    output_f.write(fmt % args)
    output_f.write("\n")


def load_mod(modName):
    try:
        real_load(modName)
    except:
        print("Error in documenting %s" % modName)
        print_exc()


def real_load(modName):
    mod = __import__("modules.%s" % modName, globals(), locals(), ['onLoad', 'onUnload'], 0)

    mod.command = command_decorator
    mod.hook = hook_decorator
    mod.timer = timer_decorator
    mod.parent_cmd = noFunc

    # Provide a way for plugins to detect they are being loaded from the documentation generator
    mod.__is_doc = True

    # Generate the header from the doc string

    output("")

    if hasattr(mod, "__info__"):
        output("# %s ( By %s ) #", modName, mod.__info__["Author"])
    else:
        output("# %s #", modName)

    if hasattr(mod, "__doc__"):
        output("%s", mod.__doc__)
    else:
        output("** No doc string found **")

    if hasattr(mod, "onLoad"):
        mod.onLoad()


output_f = open("README.md", "w")

with open("README_HEAD.md") as f:
    output_f.write(f.read())

files = glob("modules/*.py")
files.sort()

for f in files:
    f = f[8:-3]
    if f[0] == "_":
        continue

    load_mod(f)

output_f.flush()
output_f.close()
