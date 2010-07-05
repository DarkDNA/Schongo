import irc
import logging
import json



def main():
	conn = irc.IrcClient(
		server="irc.darkdna.net",
		port=6667,
		nicks=["Schongo"],
		ident="schongo",
		realname="Schongo Beever"
	);
	conn.connect()
	conn.start()
	return conn
	
if __name__ == "__main__":
	main()

