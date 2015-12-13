#!/usr/bin/python
wxycstr="""
 __      ____  ___   _  ___ 
 \ \ /\ / /\ \/ / | | |/ __|
  \ V  V /  >  <| |_| | (__ 
   \_/\_/  /_/\_\ __, |\___|        
                  |___/              

"""
"""
Script written by Alex Long (https://github.com/along528) round 'a' bout 2010
Dependencies: python v2 or later, mplayer, curses python module, curl

Download mplayer here: http://www.mplayerhq.hu/design7/dload.html
or 'brew install mplayer' 
"""


import curses
import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
import signal

import time

	

def sortplaylist(playlist):
	songcount = 0
	info = []
	inside = False
	for line in playlist:
		line.rstrip()
		if line.find('<td align="center" class="smalltext"></td>') != -1:
			inside = False
		elif inside == True:
			line = line.lstrip('\t\t<td align="left" class="smalltext">')
			line = line.rstrip('</td>')
			info[songcount-1].append(line)  
		elif line.find('<td align="center" class="smalltext" width="5%">') != -1:
			info.append([])
			songcount = songcount+1
			inside = True
	for line in playlist:
		line.rstrip()
		if line.find('START OF SHOW:') > -1:
			line = line.lstrip('\t\t<td colspan="6" align="left" class="talkset">START OF SHOW:')
			line = line.rstrip('</td>')
			dj = line
			break

	for line in playlist:
		line.rstrip()
		if line.find('Last Updated By DJ:') != -1:
			line = line.lstrip('\t\twidth="50%">Last Updated By DJ: <font color="#bb0000">&nbsp;&nbsp;&nbsp;')
			updated = line
			break

	
	return info, dj, updated

def initcurses(curses):
	#setup curses module for refreshing terminal
	curses.start_color()
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
	curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)

def updateplaylist():

	

	#display title
	wxycsplit = wxycstr.splitlines()
	count = 0
	for line in wxycsplit:
		if count == 0:
			stdscr.addstr(0,0,line,curses.color_pair(4))
		stdscr.addstr(line,curses.color_pair(1))
		count = 1
		stdscr.addstr("\n")

	
	#old link
	#cmd = "curl http://www.wxyc.info/recent.html 2>/dev/null"

	#grab html version of database
 	cmd = "curl http://www.wxyc.info/playlists/recent.html 2>/dev/null"
	www = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)

	wwwplay = www.stdout.read()
	wwwplaylist = wwwplay.splitlines() 
	playlist, dj, updated = sortplaylist(wwwplaylist)
	updated = 'Last Update: ' + updated
	stdscr.addstr(4,35,dj,curses.color_pair(1))
	stdscr.addstr(5,35,updated,curses.color_pair(1))
	
	line = 'Artist'
	line = line.ljust(35,' ')+'  '
	stdscr.addstr(7,0,line,curses.color_pair(5))
	line = 'Song'
	line = line.ljust(35,' ')+'  '
	stdscr.addstr(line,curses.color_pair(5))
	line = "Album"
	line = line.ljust(35,' ')+'  '
	stdscr.addstr(line,curses.color_pair(5))
	line = "Label                         "
	stdscr.addstr(line,curses.color_pair(5))
	stdscr.addstr("\n")
	
	for x in range(15):
		line = playlist[x][0] 
		line = line[:35].ljust(35,' ') + '  '
		stdscr.addstr(line ,curses.color_pair(1))
		line = playlist[x][1]
		line = line[:35].ljust(35,' ') + '  '
	 	stdscr.addstr(line,curses.color_pair(2))
		line = playlist[x][2]
		line = line[:35].ljust(35,' ') + '  '
		stdscr.addstr(line ,curses.color_pair(3))
		line = playlist[x][3]
		line = line[:30]
	 	stdscr.addstr(line,curses.color_pair(4) )
	 	#stdscr.addstr(line[:20] +"\t",curses.color_pair(1))
		stdscr.addstr("\n")
	
	stdscr.refresh()


try:
	#Run curses
	stdscr = curses.initscr()
	initcurses(curses)
	#grab screen for output
	stdout = open(os.devnull,'w')
	#run audio player and get the stream!
	mplayer = Popen(["mplayer","-playlist",\
	"http://wxyc.org/files/streams/wxyc-mp3.m3u"],shell=False,\
	stdin=PIPE,stderr=stdout,stdout=stdout,close_fds=True)
	#refresh playlist every 30s until shutdown
	while True:
		updateplaylist()
		time.sleep(30)
except:
	mplayer.kill()
	try:
		curses.endwin()
	except: 
		exit()
	exit() 
	
