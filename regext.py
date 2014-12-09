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


def ParsePage(layout):
	xset, yset = set(), set()
	tlines = [ ]
	objstack = list(reversed(layout._objs))
	while objstack:
		b = objstack.pop()
		if type(b) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
			objstack.extend(reversed(b._objs))  # put contents of aggregate object into stack
		elif type(b) == LTTextLineHorizontal:
			# print "Text: %s" % b.get_text()
			tlines.append(b)
		elif type(b) == LTRect or type(b) == LTLine:
			#if isLine(b, 'h', 2, 200):
			#	print "!!(%s: length=%s)" % (b.y0, (b.x1 - b.x0))
			#else:
			#	print "(%s, %s, %s, %s)" % (b.x0, b.y0, (b.x1 - b.x0), (b.y1 - b.y0))
			line = getLine(b, 10)
			if line != None:
				if line['orientation'] == 'h':
					print "Horizontal Line @%s Length=%s" % (line['pos'], line['len'])
				else:
					print "Vertical   Line @%s Length=%s" % (line['pos'], line['len'])
		else:
			print "Unrecognized type: %s" % type(b)


def isLine(b, orientation='hv', max_line_width=2, min_length=0, max_length=1000):
	if 'h' in orientation and (b.y1 - b.y0) <= max_line_width:
		if (b.x1 - b.x0) >= min_length and (b.x1 - b.x0) <= max_length:
			return True
	if 'v' in orientation and (b.x1 - b.x0) <= max_line_width:
		if (b.y1 - b.y0) > min_length and (b.y1 - b.y0) < max_length:
			return True
	return False

def getLine(b, max_line_width=2):
	line = {}
	if (b.y1 - b.y0) <= max_line_width:
		return {'orientation': 'h', 'pos': b.y0, 'len': (b.x1 - b.x0)}
	elif (b.x1 - b.x0) <= max_line_width:
		return {'orientation': 'v', 'pos': b.x0, 'len': (b.y1 - b.y0)}
	else:
		return None

def main():
	fp = open('pdf/stm_test.pdf', 'rb')
	outfp = open('txt/lpc_test.txt', 'wb')

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
		ParsePage(layout)

	fp.close()
	outfp.close()

if __name__ == "__main__":
	main()
