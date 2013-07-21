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


from pdfminer.pdfparser import PDFParser, PDFDocument, PDFNoOutlines, PDFSyntaxError
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import \
	LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTTextLineHorizontal, \
	LTTextBoxHorizontal, LTChar, LTRect, LTLine, LTAnon

from logger import Logger

class Parser():
	""" Parser
		basic PDF Parser based on the pdf miner libraries
		this class handles all the pdf miner specific stuff
	"""

	def __init__(self, logger=None):
		if logger == None:
			self.log = Logger()
		else:
			self.log = logger
		self.boxes = []
		self.texts = []
		self.lines = []
		self.hLines = []
		self.vLines = []
		self.rectangles = []
		self.max_line_width = 2

	def parse(self, file_name):
		"""
		parse file
		inspired by:
		http://blog.scraperwiki.com/2012/06/25/pdf-table-extraction-of-a-table/
		"""
		fp = open(file_name, 'rb')
		parser = PDFParser(fp)
		doc = PDFDocument()
		parser.set_document(doc)
		doc.set_parser(parser)

		doc.initialize("")
		rsrcmgr = PDFResourceManager()
		laparams = LAParams()
		device = PDFPageAggregator(rsrcmgr, laparams=laparams)
		interpreter = PDFPageInterpreter(rsrcmgr, device)

		for n, page in enumerate(doc.get_pages()):
			interpreter.process_page(page)
			layout = device.get_result()
			self._parsePage(layout)
		fp.close()

	def _parsePage(self, layout):
		objstack = list(reversed(layout._objs))
		while objstack:
			b = objstack.pop()
			if type(b) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
				objstack.extend(reversed(b._objs))  # put contents of aggregate object into stack
			elif type(b) in [LTTextLineHorizontal, LTRect, LTLine]:
				box = Box(b)
				self.boxes.append(box)
				if box.isText():
					self.texts.append(box)
				if box.isLine(self.max_line_width):
					self.lines.append(box)
				if box.isHorizontalLine(self.max_line_width):
					self.hLines.append(box)
				if box.isVerticalLine(self.max_line_width):
					self.vLines.append(box)
				if box.isRectangle(self.max_line_width):
					self.rectangles.append(box)
				self.log.debug(str(box))


class Box():
	""" Box
	describes box objects found in pdf file
	lines, rectangles, text
	"""

	OBJECTS = [LTRect, LTLine, LTTextLineHorizontal]

	def __init__(self, obj):
		if type(obj) not in self.OBJECTS:
			assert False, "Box can only be created from %s" % self.OBJECTS
		self.x0 = obj.x0
		self.x1 = obj.x1
		self.y0 = obj.y0
		self.y1 = obj.y1
		self.text = None
		if type(obj) == LTTextLineHorizontal:
			self.text = obj.get_text()

	@property
	def width(self):
		return self.x1 - self.x0

	@property
	def height(self):
		return self.y1 - self.y0

	def isLine(self, max_line_width=2):
		"""isLine
		checks if this is a line by checking if the minimum with is
		smaller or equal to the max_line_width
		"""
		return min(self.width, self.height) < max_line_width

	def isHorizontalLine(self, max_line_width=2):
		"""isHorizontalLine
		checks if this is a horizontal line by checking if the box height is
		smaller or equal to the max_line_width
		"""
		return self.height < max_line_width

	def isVerticalLine(self, max_line_width=2):
		"""isVerticalLine
		checks if this is a vertival line by checking if the box width is
		smaller or equal to the max_line_width
		"""
		return self.width < max_line_width

	def isRectangle(self, max_line_width=2):
		"""isRectangle
		returns true if this is not a line
		"""
		return not self.isLine(max_line_width)

	def isText(self):
		return self.text != None

	def __unicode__(self):
		s = "@(%.2f,%.2f)->(%.2f,%.2f)" % (self.x0, self.y0, self.x1, self.y1)
		s += "\nPDFBox: "
		if self.isHorizontalLine():	s += "Horizontal Line"
		if self.isVerticalLine():	s += "Vertical Line"
		if self.isRectangle():		s += "Rectangle"
		s += " [%.2f x %.2f]" % (self.width, self.height)
		s += "\nText: %s" % self.text
		return s

	def __str__(self):
		return unicode(self).encode('utf-8')
