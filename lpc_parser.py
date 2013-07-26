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

from parser import Parser, Box
from logger import Logger

class LPCParser(Parser):
	""" LPCParser
		Parser for LPC datasheets
	"""


	def __init__(self, logger=None):
		Parser.__init__(self, logger)
		self.laparams.char_margin = 1.0
		self.first_section = True

	def _checkSectionStart(self, box):
		"""_checkSectionStart
		checks if this box presents the start of a content section
		returns (start_before_box, start_after_box) as booleans
		"""
		# TODO: use good regex
		if box.text != None and box.text.startswith("Table"):
			return True
		return False

	def _checkSectionEnd(self, box):
		"""_checkSectionEnd
		checks if this box presents the end of a content section
		returns (break_before_box, break_after_box) as booleans
		"""
		# TODO: use good regex
		if box.text != None and box.text.startswith("Table"):
			return True
		return False

	def _processSection(self):
		"""_processSection
		process tables that were found by the section end/start methods
		"""
		# HACK: Process only first Section
		if self.first_section:
			self.first_section = False
			title = ""		# the title text of the table
			text = []		# all text objects in table
			lines = []		# all lines that make up the table
			vLines = []		# x0 position of vertical lines
			# create stack
			stack = list(reversed(self.boxes))
			self.boxes = []
			# parse text in front of table:
			box = stack.pop()
			while box.isText():
				title += box.text + " "
				box = stack.pop()
			self.log.debug("Title: %s" % title)
			# check if box is table start line
			if not box.isHorizontalLine(1) or not box.checkWidth(383):
				self.log.error("Invalid Table! Needs to start with 383 long horizontal line.")
			lines.append(box)
			vLines.append(box.x0)	# left-most vertical line
			vLines.append(box.x1)	# right-most vertical line
			# try to find the headings
			box = stack.pop()
			if not box.isText():
				self.log.error("Invalid Table! expected next element to be text.")
			headings = self.getObjectsInLineWith(box)
			headings = [h for h in headings if h.isText()]
			# deduce vertical lines from headings
			for t in headings:
				text.apend(t)
				if t != box:
					vLines.append(t.x0)
				#self.log.info("%s: '%s'" % (t.x0, t.text))
			# find remaining lines in table
			while len(stack) > 0:
				if box.isHorizontalLine(1):
					lines.append(box)
				elif box.isText():
					text.append(box)
				box = stack.pop()
			# create vertical lines
			width = .23
			y0 = lines[0].y0
			y1 = lines[-1].y1
			for x0 in vLines:
				lines.append(Box(x0,y0,x0 + width,y1))
			# parse tabe
			self.parseTable(lines, text)



if __name__ == "__main__":
	l = Logger()
	l.setLogLevel("debug")
	p = LPCParser(l)
	p.parse("pdf/lpc_test_3_page.pdf")
