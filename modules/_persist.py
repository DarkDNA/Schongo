"""Provides and implements the __persist__ module function"""


import pickle

global persist
persist = {}

# Meta information
__info__ = {
	"Author": "Amanda Cameron",
	"Version": "0.1",
	"Dependencies": []
}

# Support functions

def load_persist():
	global persist
	try:
		f = open("data/mod_persist.pickle", "rb")
		persist = pickle.load(f)
		f.close()
		logger.info("Persist loaded: %s", persist)
	except:
		logger.warn("Failed to load persist data")
		pass

def save_persist():
	global persist
	logger.info("Saving persist: %s", persist)
	f = open("data/mod_persist.pickle", "wb")
	pickle.dump(persist, f)
	f.flush()
	f.close()
	logger.info("Done.")

# Plugin Events

def onLoad():
	load_persist()

	@hook("module_preload")
	def preload_hook(modInfo):
		global persist

		mod = modInfo.module
		modName = modInfo.name
		
		if modName in persist and hasattr(mod, "__persist__"):
			for i in mod.__persist__:
				if i in persist[modName]:
					setattr(mod, i, persist[modName][i])

	@hook("module_postunload")
	def unload_hook(modInfo):
		global persist

		mod = modInfo.module
		modName = modInfo.name

		if hasattr(mod, "__persist__"):
			persist[modName] = {}
			for i in mod.__persist__:
				persist[modName][i] = getattr(mod, i)

def onUnload():
	save_persist()
