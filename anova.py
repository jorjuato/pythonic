#
#	Anova.py -- a python module for performing simple ANOVAs
#	Author:  Paul M. Magwene
#	Revision:  09 November 1999

""" A module for doing simple ANOVAs


-----------------------------------------------------------------------------
(c) Copyright by Paul M. Magwene, 1999 (mailto:paul.magwene at yale.edu)

    Permission to use, copy, modify, and distribute this software and
its
    documentation for any purpose and without fee or royalty is hereby
granted,
    provided that the above copyright notice appear in all copies and
that
    both that copyright notice and this permission notice appear in
    supporting documentation or portions thereof, including
modifications,
    that you make.

    THE AUTHOR PAUL M. MAGWENE DISCLAIMS ALL WARRANTIES WITH REGARD TO
    THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND
    FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
    INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
RESULTING
    FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
    NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
    WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !

"""

__version__ = '0.2'

#----------------------------------------------------------------------------

import sys, copy
import Numeric

#----------------------------------------------------------------------------

def mean(data):
    """Returns the arithmetic mean of a sequence of variables.

    When matrix is passed in, calculates means over columns.
    """
    data = Numeric.array(data)
    return Numeric.add.reduce(data)/len(data)

def SS(data):
    """Returns the sum of the squared deviates."""
    data = Numeric.array(data)
    return Numeric.add.reduce((deviates(data))**2)

def collapse(inlist, type=type, integers = xrange(sys.maxint), endoflist=IndexError):
	"""Non destructively flatten a list hierarchy to a single level.

	Non-recursive.
	"""
	outlist = copy.copy(inlist)
	try:
		for ind in integers :
			while isinstance(outlist[ind],list):
				outlist[ind:ind+1] = outlist[ind]
	except endoflist:
		return outlist

class Anova:

	def __init__ (self,groups=[]):
		self._groups = []
		self._groups = groups

	def groups(self,groups=[]):
		self._groups = groups

	def groups(self):
		return self._groups

	def numGroups(self):
		return len(self._groups)

	def grandMean(self):
		temp = self._groups[:]
		return mean(collapse(temp))

	def groupMeans(self):
		result = []
		for g in self._groups:
			result.append(mean(g))
		return result

	def SSwin(self):
		sswin = 0.0
		for g in self._groups:
			sswin = sswin + SS(g)
		return sswin

	def SSmeans(self):
		return SS(self.groupMeans())

	def SSamong(self):
		return self.SStot() - self.SSwin()

	def SStot(self):
		temp = self._groups[:]
		return SS(collapse(temp))

	def MSwin(self):
		DFsum = 0.0
		for g in self._groups:
			DFsum = DFsum + (len(g) - 1.0)
		return self.SSwin()/DFsum

	def MSamong(self):
		return self.SSamong()/(self.numGroups() - 1.0)

	def MStot(self):
		return self.SStot()/((self.numGroups() * self.avgSampleSz()) - 1.0)

	def Fs(self):
		return self.MSamong()/self.MSwin()

	def avgSampleSz(self):
		a = self.numGroups()
		sum_ni = 0
		sum_ni2 = 0
		for g in self._groups:
			ni = len(g)
			sum_ni = sum_ni + ni
			sum_ni2 = sum_ni2 + ni**2
		sum_ni = Float(sum_ni)
		sum_ni2 = Float(sum_ni2)
		return (1.0/(a-1))*(sum_ni - (sum_ni2 / sum_ni))

	def _sum_ni(self):
		sum_ni = 0
		for g in self._groups:
			sum_ni = sum_ni + len(g)
		return sum_ni

	def DFamong(self):
		return self.numGroups() - 1

	def DFwin(self):
		return self._sum_ni() - self.numGroups()

	def DFtot(self):
		return self._sum_ni() - 1

	def anovaTable(self):
		header = "Source\tdf\tSS\t\tMS\t\tF\n" + (60*'-') + '\n'
		line1 = "among\t%-7d %-15.5f %-15.5f %-15.5f\n" % \
				(self.DFamong(),self.SSamong(),self.MSamong(),self.Fs())
		line2 = "within\t%-7d %-15.5f %-15.5f\n" % \
				(self.DFwin(),self.SSwin(),self.MSwin())
		line3 = "total\t%-7d %-15.5f\n" % (self.DFtot(),self.SStot())
		table = header + line1 + line2 +line3
		return table

if __name__ == '__main__':
	#test data from Sokal & Rohlf(1995), Biometry(3rd edition) table 9.1,
    #p. 210
	print "\n\n\nSample output of Anova.py \n\n"
	print "\nTest data from Sokal & Rohlf (1994), table 9.1, p. 210\n\n"
	A = [380 , 376 , 360 , 368 , 372 , 366 , 374 , 382]
	B = [350 , 356 , 358 , 376 , 338 , 342 , 366 , 350 , 344 , 364]
	C = [354 , 360 , 362 , 352 , 366 , 372 , 362, 344 , 342 , 358 , 351 , 348 , 348]
	D = [376 , 344 , 342 , 372 , 374 , 360]

	av = Anova([A,B,C,D])

	print "# of groups: ", av.numGroups()
	print "group A: ", A
	print "group B: ", B
	print "group C: ", C
	print "group D: ", D
	print ""
	print "group means: ", av.groupMeans()
	print "grand mean: ", av.grandMean()
	print ""
	print "anova table --"
	print av.anovaTable()
