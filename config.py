from ConfigParser import RawConfigParser,NoSectionError


class ConfigSection:
	cfg = None
	section = None

	def __init__(self, cfg, sec):
		self.cfg = cfg
		self.section = sec

	def get(self, opt):
		return self.cfg.get(self.section, opt)

	def getint(self, opt):
		return self.cfg.getint(self.section, opt)

	def getfloat(self, opt):
		return self.cfg.getfloat(self.section, opt)

	def getboolean(self, opt):
		return self.cfg.getboolean(self.section, opt)

	def getlist(self, opt, char=','):
		return self.cfg.get(self.section, opt).split(char)

	def set(self, opt, val):
		self.cfg.set(self.section, opt, val)

	def clear(self, opt=None):
		if opt is None:
			self.cfg.remove_section(self.section)
			self.cfg.add_section(self.section)
		else:
			self.cfg.remove_option(self.section, opt)

	def items(self):
		return self.cfg.items(self.section)
		


class Config(RawConfigParser):

	def __init__(self, *a, **kw):
		RawConfigParser.__init__(self, *a, **kw);

	def get_section(self, section, createIfNone=False):
		if not self.has_section(section):
			if createIfNone:
				self.add_section(section)
			else:
				raise NoSectionError, "No such section %s" % section

		return ConfigSection(self, section)
