"""
  SAFESTRUCT Version 1.0
  February 4, 1999

This class traps accesses to attributes and raises an exception
when an assignment to a non-previously-existing attribute is
performed. The idea is that of a "safe structure", as in
C++ where each member of a class is declared at compile time
and assignments to non-existent members cannot be made at
run time. The safe structure guards against programming
errors wherein attribute names are mispelled, leading to
quiet runtime errors.

There are two classes defined here, TrappingStruct and
NontrappingStruct. Both present the same interface but the
latter does no attribute checking. It is meant to be used
once the code is debugged, since it is faster.

The SafeStruct member is either set equal to TrappingStruct
or NontrappingStruct (possibly by the SetDebug function) to
easily switch from safe accesses to faster accesses by just
changing one thing in one file.

See the test code at the bottom for example usage.

Andrew Sterian
asterian@umich.edu
"""

class TrappingStruct:
  def __init__(self, members={}):
    for name,value in members.items():
      self.__dict__[name] = value

  def __setattr__(self, name, value):
    if not self.__dict__.has_key(name):
      raise AttributeError, 'structure %s has no member "%s"' % (self.__class__.__name__, name)

    self.__dict__[name] = value

  def __delattr__(self, name):
    if not self.__dict__.has_key(name):
      raise AttributeError, 'structure %s has no member "%s"' % (self.__class__.__name__, name)

    del self.__dict__[name]

  def add_attributes(self, dict):
    "Allows bypass of the trapping mechanism to add members"
    for name, value in dict.items():
      self.__dict__[name] = value

class NontrappingStruct:
  def __init__(self, members={}):
    for name,value in members.items():
      self.__dict__[name] = value

  def add_attributes(self, dict):
    "Allows bypass of the trapping mechanism to add members"
    for name, value in dict.items():
      self.__dict__[name] = value

##########################################

# By default, safe accesses are enabled
SafeStruct = TrappingStruct

def SetDebug(onoff):
  global SafeStruct

  if onoff:
    SafeStruct = TrappingStruct
  else:
    SafeStruct = NontrappingStruct

# Set debug state here for entire application
SetDebug(1)

###################################

if __name__ == "__main__":
  print 'Testing illegal access without safety...'
  print

  SetDebug(0)

  class TestClass1(SafeStruct):
    def __init__(self):
      SafeStruct.__init__(self, {'field1': 0, 'field2': 0})

  T1 = TestClass1()
  T1.field1 = 1
  T1.FIELD2 = 2   # error, no exception
  print 'field1: %d  field2: %d' % (T1.field1, T1.field2)
  print

  print 'Testing illegal access with safety...'
  print

  SetDebug(1)

  class TestClass2(SafeStruct):
    def __init__(self):
      SafeStruct.__init__(self, {'field1': 0, 'field2': 0})

  T2 = TestClass2()
  try:
    T2.field1 = 3
    T2.FIELD2 = 4   # error, with exception
  except AttributeError, detail:
    print 'Exception: %s' % detail
  else:
    print "Huh? How come we didn't get an exception???"
