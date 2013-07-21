#!/usr/bin/env python
#
# Copyright (C) 2013 eKiwi
#
# This file is part of regexT.  regexT is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import sys, os

class Logger:
	# Terminal Escape Sequences
	COLOR_END     = '\033[0m'
	COLOR_BLACK   = '\033[30m'
	COLOR_RED     = '\033[31m'
	COLOR_GREEN   = '\033[32m'
	COLOR_YELLOW  = '\033[33m'
	COLOR_BLUE    = '\033[34m'
	COLOR_MAGENTA = '\033[35m'
	COLOR_CYAN    = '\033[36m'
	COLOR_WHITE   = '\033[37m'

	# Define Debug Colors
	COLOR_DEBUG   = COLOR_WHITE
	COLOR_INFO    = COLOR_CYAN
	COLOR_WARN    = COLOR_YELLOW
	COLOR_ERROR   = COLOR_RED

	# Log Level
	LOG_LEVEL = {
		'debug':   0,
		'info':    1,
		'warning': 2,
		'warn':    2,
		'error':   3,
		'err':     3,
		'disabled': 4 }


	def __init__(self, log_level='err'):
		self.stderr_color = self._checkColorSupport(sys.stderr)
		self.stdout_color = self._checkColorSupport(sys.stdout)
		# Default is Error
		self.setLogLevel(log_level)
		self.line_info = True # to be implemented

	def debug(self, s):
		if self.log_level <= self.LOG_LEVEL['debug']:
			self.write("Debug: " + s, self.COLOR_DEBUG, sys.stdout)

	def info(self, s):
		if self.log_level <= self.LOG_LEVEL['info']:
			self.write("Info: " + s, self.COLOR_INFO, sys.stdout)

	def warn(self, s):
		if self.log_level <= self.LOG_LEVEL['warn']:
			self.write("Warn: " + s, self.COLOR_WARN, sys.stderr)

	def error(self, s):
		if self.log_level <= self.LOG_LEVEL['error']:
			self.write("Error: " + s, self.COLOR_ERROR, sys.stderr)

	def write(self, string, color=None, stream=sys.stdout):
		# Check Color Support
		if stream == sys.stdout and not self.stdout_color:
			color = None
		if stream == sys.stderr and not self.stderr_color:
			color = None
		# Print Color
		if color != None:
			stream.write(color)
		# Print String
		stream.write(string)
		# End Color
		if color != None:
			stream.write(self.COLOR_END)
		# Line Ending
		stream.write(os.linesep)

	def setLogLevel(self, new_level):
		if isinstance(new_level, int):
			self.log_level = new_level
		elif isinstance(new_level, basestring):
			new_level = new_level.lower()
			if new_level in self.LOG_LEVEL:
				self.log_level = self.LOG_LEVEL[new_level]

	def isLogLevel(self, log_level):
		# Try to Convert Log Level String to Int
		if isinstance(log_level, basestring):
			log_level = log_level.lower()
			if log_level in self.LOG_LEVEL:
				log_level = self.LOG_LEVEL[log_level]
		# Check Log Level
		if isinstance(log_level, int):
			if self.log_level <= log_level:
				return True
		return False

	def _checkColorSupport(self, stream):
		if hasattr(stream, "isatty") and stream.isatty() or \
			('TERM' in os.environ and os.environ['TERM']=='ANSI'):
			return True
		else:
			return False
