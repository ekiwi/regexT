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
		self.max_line_width = 2
		self.y_offset = 0 # offset on extended page
		"""
		The derrived, document specific parsers will operate
		on this lists that will contain all elements found on an
		"extended page" in increasing x0 order.
		"""
		self.boxes = []
		self.texts = []
		self.lines = []
		self.hLines = []
		self.vLines = []
		self.rectangles = []


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
			self.log.debug("Page #%s, mediabox=%s, cropbox=%s" % (n, page.mediabox, page.cropbox))
			interpreter.process_page(page)
			layout = device.get_result()
			boxes = self._parsePage(layout, page.cropbox[3])
			self._processPage(boxes, page.cropbox[3])
		fp.close()

	def _parsePage(self, layout, cropbox_height):
		boxes = []
		objstack = list(reversed(layout._objs))
		while objstack:
			b = objstack.pop()
			if type(b) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
				objstack.extend(reversed(b._objs))  # put contents of aggregate object into stack
			elif type(b) in [LTTextLineHorizontal, LTRect, LTLine]:
				boxes.append(Box(b, cropbox_height))
		return boxes

	def _processPage(self, boxes, page_height):
		"""processPage
		"""
		boxes = sorted(boxes, key=lambda box: box.y0)
		for box in boxes:
			if self._checkEndContent(box):
				self._processContent()
				#TODO: Add box before or after process Content?
				self.y_offset = 0
				# reset lists
				self.boxes = []
				self.texts = []
				self.lines = []
				self.hLines = []
				self.vLines = []
				self.rectangles = []
			box.moveY(self.y_offset)
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

	def _checkEndContent(self, box):
		"""_checkEndContent
		returns true if end of content that will be parsed in one go is reached
		"""
		self.log.error("_checkEndContent needs to be overridden by derived class")
		return False

	def _processContent(self):
		"""_processContent
		process accumulated content
		needs to be overridden by derived class
		"""
		self.log.error("_processContent needs to be overridden by derived class")


class Box():
	""" Box
	describes box objects found in pdf file
	lines, rectangles, text
	"""

	OBJECTS = [LTRect, LTLine, LTTextLineHorizontal]

	def __init__(self, obj, cropbox_height):
		"""
		the cropbox_height is needed in order to transform the y coordinates
		"""
		if type(obj) not in self.OBJECTS:
			assert False, "Box can only be created from %s" % self.OBJECTS
		self.x0 = obj.x0
		self.x1 = obj.x1
		self.y0 = cropbox_height - obj.y0
		self.y1 = cropbox_height - obj.y1
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

	def moveX(self, x):
		self.x0 += x
		self.x1 += x

	def moveY(self, y):
		self.y0 += y
		self.y1 += y

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
