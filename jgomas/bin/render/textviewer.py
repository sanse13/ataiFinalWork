#!/usr/bin/env python
# -*- coding: UTF8 -*-
import curses
import time
import socket
import sys, traceback
import copy
import os

objective_x = -1
objective_y = -1
allied_base = None
axis_base = None
graph = {}
stdscr = None
pad = None
f = None
agents = {}
dins = {}
factor = 2

def agl_parse(data):
	global allied_base
	global axis_base
	global objective_x
	global objective_y
	global agents
	
	f.write("\nAGL_PARSE\n")
	agl = data.split()
	nagents = int(agl[1])
	agl = agl[2:]
	separator = nagents*15
	f.write("NAGENTS = %s\n"%(str(nagents)))
	agent_data = agl[:separator]
	din_data = agl[separator:]
	f.write("AGENT_DATA:"+str(agent_data))
	for i in range(nagents):
		agents[agent_data[0]] = {"type":agent_data[1], "team":agent_data[2], "health":agent_data[3], "ammo":agent_data[4], "carrying":agent_data[5], "posx":agent_data[6].strip("(,)"), "posy":agent_data[7].strip("(,)"), "posz":agent_data[8].strip("(,)")}
		f.write("AGENT "+str(agents[agent_data[0]]))
		agent_data = agent_data[15:]
	
	f.write("DIN_DATA:"+str(din_data))
	ndin = int(din_data[0])	
	f.write("NDIN = %s\n"%(str(ndin)))
	din_data = din_data[1:]
	for din in range(ndin):
		dins[din_data[0]] = {"type":din_data[1],"posx":din_data[2].strip("(,)"),"posy":din_data[3].strip("(,)"),"posz":din_data[4].strip("(,)")}
		f.write("DIN "+str(dins[din_data[0]]))
		din_data = din_data[5:]

	

def draw():
	global agents
	global factor
	
	f.write("DRAW")
	# Draw Map
	for k,v in graph.items():
		f.write("DRAW "+str(k))
		try:
			newline = ""
			for char in v: newline += char*factor
			stdscr.addstr(k, 0, str(newline))
		except Exception, e:
			f.write("\nEXCEPTION IN DRAW(1): "+str(e)+"\n")

	# Draw bases and objective
	try:
		#print "ALLIED BASE: ",str(allied_base)
		curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)  # ALLIED BASE
		for y in range(int(allied_base[1]), int(allied_base[3])):
			for x in range(int(allied_base[0])*factor, int(allied_base[2])*factor):
				f.write("BASE "+str(y)+" "+str(x))
				stdscr.addch(y,x," ",curses.color_pair(4))
		curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLUE)  # AXIS BASE
		
		for y in range(int(axis_base[1]), int(axis_base[3])):
			for x in range(int(axis_base[0])*factor, int(axis_base[2])*factor):
				f.write("BASE "+str(y)+" "+str(x))
				stdscr.addch(y,x," ",curses.color_pair(3))
		curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW) # DINOBJECTS
		#stdscr.addch(objective_y, objective_x*factor, "F", curses.color_pair(2))
		#f.write("OBJECTIVE "+str(objective_y)+" "+str(objective_x))
		for k,v in dins.items():
			# Type
			if v["type"] == "1001": c = "M"
			elif v["type"] == "1002": c = "A"
			elif v["type"] == "1003": c = "F"
			else: c = "X"
			y = int(float(v["posz"]) / 8)
			x = int(float(v["posx"]) / (8/factor))
			stdscr.addch(y,x,c,curses.color_pair(2))
		
		curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_RED)  # ALLIED
		curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)  # AXIS
		curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)  # OTHER / DEAD
		stats_allied = ""
		stats_axis = ""
		for k,v in agents.items():
			# Type
			if v["type"] == "0": c = "X"
			elif v["type"] == "1": c = "*"
			elif v["type"] == "2": c = "+"
			elif v["type"] == "3": c = "Y"
			elif v["type"] == "4": c = "^"
			else: c = "X"
			# Team (or Carrier)
			if v["carrying"] == "1": t = 2
			elif v["team"] == "100": t = 5
			elif v["team"] == "200": t = 6
			else: t = 1
			# Draw in map
			y = int(float(v["posz"]) / 8)
			x = int(float(v["posx"]) / (8/factor))
			if int(v["health"]) > 0:
				stdscr.addch(y,x,c,curses.color_pair(t))  # Alive
			else:
				stdscr.addch(y,x,"D",curses.color_pair(7))  # Dead
			# Write stats
			if int(v["health"]):
				if v["team"] == "100":				
					#stats_allied += " | " + k + " " + v["health"] + " " + v["ammo"] + " "
					if int(v["health"]) > 0:
						stats_allied += " | %s %s %03d %03d "%(c,k,int(v["health"]),int(v["ammo"]))
					else:
						stats_allied += " | %s %s --- --- "%(c,k)
				elif v["team"] == "200":
					#stats_axis += k + " " + v["health"] + " " + v["ammo"] + " "
					if int(v["health"]) > 0:
						stats_axis += " | %s %s %03d %03d "%(c,k,int(v["health"]),int(v["ammo"]))
					else:
						stats_axis += " | %s %s --- --- "%(c,k)
		blank = "                                                                                 "
		stdscr.addstr(33, 1, blank)
		stdscr.addstr(33, 1, str(stats_allied), curses.color_pair(5))
		stdscr.addstr(34, 1, blank)
		stdscr.addstr(34, 1, str(stats_axis), curses.color_pair(6))
	except Exception, e:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		f.write("\nEXCEPTION IN DRAW: "+str(e)+ str(exc_type) + str(exc_value) + str(exc_traceback) + "\n")
	
	# Refresh screen
	try:
		stdscr.refresh()
	except:
		pass
		

def loadMap(mapname):
	global allied_base
	global axis_base
	global objective_x
	global objective_y
	
	mapf = open("../data/maps/"+mapname+"/"+mapname+".txt", "r")
	for line in mapf.readlines():
		if "JADE_OBJECTIVE" in line:
			l = line.split()
			objective_x = copy.copy(int(l[1]))
			objective_y = copy.copy(int(l[2]))
			f.write("OBJECTIVE:"+str(objective_x)+" "+str(objective_y))
		elif "JADE_SPAWN_ALLIED" in line:
			l = line.split()
			l.pop(0)
			allied_base = copy.copy(l)
			f.write("ALLIED_BASE:"+str(l))
		elif "JADE_SPAWN_AXIS" in line:
			l = line.split()
			l.pop(0)
			axis_base = copy.copy(l)
	mapf.close()
	f.write("MAPF LOADED\n")
	
	cost = open("../data/maps/"+mapname+"/"+mapname+"_cost.txt", "r")
	y = 0
	for line in cost.readlines():
		graph[y] = line.strip("\r\n")
		y += 1
	cost.close()
	#print "GRAPH",str(graph)
	f.write(str(graph))

	

# Main
f = open("/tmp/tv.log", "w")
f.write("LOG\n")

# Init curses
curses_up = False
stdscr = curses.initscr()
curses.start_color()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)
#curses.curs_set(0)
curses_up = True
#stdscr.addstr("CURSES OPEN\n")
#stdscr.refresh()
#pad = curses.newpad(32,32)

try:
	# Init socket
	if len(sys.argv) < 2:
		ADDRESS = "localhost"
		PORT = 8001
#	stdscr.addstr("ADDRESS: %s\n"%(ADDRESS))
#	stdscr.addstr("PORT: %s\n"%(str(PORT)))	
#	stdscr.refresh()
	f.write("ADDRESS: %s\n"%(ADDRESS))
	f.write("PORT: %s\n"%(str(PORT)))
	s = None
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if s:
		#time.sleep(1)
		s.connect((ADDRESS, PORT))
		rfile = s.makefile('rb', -1)
		wfile = s.makefile('wb', 0)
#		stdscr.addstr("SOCKET OPEN %s\n"%(str(s)))
#		stdscr.refresh()
		f.write("SOCKET OPEN %s\n"%(str(s)))
		data = rfile.readline()
		f.write("Server sent: %s\n"%(data))
#		stdscr.addstr("Server sent: %s\n"%(data))
#		stdscr.refresh()
		wfile.write("READY\n")
		bLoop = True
		while bLoop:
			data = ""
			data = rfile.readline()			
			#char = ""			
#			while char != "\n":
#				data += char
#				char = s.recv(1)
			f.write("Server sent: %s\n"%(data))
#			stdscr.addstr("Server sent: %s\n"%(data))
#			stdscr.refresh()
			if "COM" in data[0:5]:
				if "Accepted" in data:
					pass
				elif "Closed" in data:
					bLoop = False
			elif "MAP" in data[0:5]:
#				print "MAP MESSAGE:",str(data)
				f.write("MAP MESSAGE: %s\n"%(data))
#				stdscr.addstr("MAP MESSAGE: %s\n"%(data))
#				stdscr.refresh()
				p = data.split()
				mapname = p[2]
				f.write("MAPNAME: %s\n"%(mapname))
				loadMap(mapname)
#				stdscr.addstr("MAPNAME: %s\n"%(mapname))
#				stdscr.refresh()
			elif "AGL" in data[0:5]:
				f.write("\nAGL\n")
				agl_parse(data)
			elif "TIM" in data[0:5]:
				pass
			elif "ERR" in data[0:5]:
				pass
			else:
				# Unknown message type
				pass
			draw()

		# Close socket
		del rfile
		del wfile
		s.close()

	# Write things to screen
	"""
	stdscr.addstr("HOLA MUNDO")
	stdscr.refresh()
	time.sleep(5)
	"""

except Exception, e:
	# Terminate
	print "Exception", str(e)
	if s:
		s.send("QUIT\n")
		s.close()
	if curses_up:
		curses.nocbreak(); stdscr.keypad(0); curses.echo()
		curses.endwin()
		curses_up = False
try:	
  if curses_up:
	# Terminate curses
	curses.nocbreak(); stdscr.keypad(0); curses.echo()
	curses.endwin()
	curses_up = False
except Exception, e:
	print "Exception", str(e)
finally:
	f.close()
	os.system("reset")
	sys.exit(0)
