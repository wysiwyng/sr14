#!/usr/bin/python

import ConfigParser

parser = ConfigParser.ConfigParser()
cfile = open("./mai-bot.cfg", 'w')

slots = raw_input("slots: ")
tokens = raw_input("token-order: ")

parser.add_section("mai-bot")
parser.set("mai-bot", "slots", slots)
parser.set("mai-bot", "token-order", tokens)
parser.write(cfile)
cfile.close()
