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

from parser import Parser
from logger import Logger

class LPCParser(Parser):
	""" LPCParser
		Parser for LPC datasheets
	"""


	def __init__(self, logger=None):
		Parser.__init__(self, logger)

	def _checkSectionStart(self, box):
		"""_checkSectionStart
		checks if this box presents the start of a content section
		returns (start_before_box, start_after_box) as booleans
		"""
		# TODO: use good regex
		if box.text != None and box.text.startswith("Table"):
			return True
		return True

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
		process accumulated content
		needs to be overridden by derived class
		"""
		self.log.info("_processSection of LPCParser called")



if __name__ == "__main__":
	l = Logger()
	l.setLogLevel("debug")
	p = LPCParser(l)
	p.parse("pdf/lpc_test_3_page.pdf")
