"""
Various ways of permuting a list of lists (a.k.a. Cartesian product).
The permutation is returned as a list of tuples.

For example:

    permute( [ [1,2], [3,4,5] ] ) gives
       [(1,3), (2,3), (1,4), (2,4), (1,5), (2,5)]
"""

def permute(Lists):
  import operator
  if Lists:
    result = map(lambda I: (I,), Lists[0])

    for list in Lists[1:]:
      curr = []
      for item in list:
        new = map(operator.add, result, [(item,)]*len(result))
        curr[len(curr):] = new
      result = curr
  else:
    result = []

  return result

# This version was written by Tim Peters and is somewhat faster,
# especially for large numbers of small lists.
def permute2(seqs):
    n = len(seqs)
    if n == 0:
        return []
    if n == 1:
        return map(lambda i: (i,), seqs[0])
    # find good splitting point
    prods = []
    prod = 1
    for x in seqs:
        prod = prod * len(x)
        prods.append(prod)
    for i in range(n):
        if prods[i] ** 2 >= prod:
            break
    n = min(i + 1, n - 1)
    a = permute2(seqs[:n])
    b = permute2(seqs[n:])
    sprayb = []
    lena = len(a)
    for x in b:
        sprayb[len(sprayb):] = [x] * lena
    import operator
    return map(operator.add, a * len(b), sprayb)

if __name__ == "__main__":
  import time
  import random
  import math
  import operator

  N = 1e3   # Approximate number of items in the permutations

  funcs = [permute, permute2]

  Times = {}
  map(operator.setitem, [Times]*len(funcs), funcs, [0]*len(funcs))

  print 'Testing small numbers of large lists...'
  for i in range(10):
    print '.',
    listLen = random.randint(2,5)
    TheList = []
    eachListLen = int(math.pow(N, 1.0/listLen) + 0.5)
    for ix in range(listLen):
      TheList.append([0] * eachListLen)

    for func in funcs:
      tic = time.clock()
      result = apply(func, (TheList,))
      toc = time.clock()
      Times[func] = Times[func] + toc-tic

  print
  for func in funcs:
    print '%s: %g' % (func.__name__, Times[func])

  map(operator.setitem, [Times]*len(funcs), funcs, [0]*len(funcs))
  print 'Testing large numbers of small lists...'

  for i in range(10):
    print '.',
    listLen = random.randint(20,30)
    TheList = []
    eachListLen = N
    while eachListLen > 1:
      TheList.append([0,0])
      eachListLen = eachListLen / 2
    for ix in range(len(TheList), listLen):
      TheList.append([0])

    for func in funcs:
      tic = time.clock()
      result = apply(func, (TheList,))
      toc = time.clock()
      Times[func] = Times[func] + toc-tic
    
  print
  for func in funcs:
    print '%s: %g' % (func.__name__, Times[func])

  print 'Checking correctness...'
  def ctest(func):
    def listeq(L1,L2):
      L1.sort()
      L2.sort()
      return L1==L2

    try:
      assert apply(func, ([],)) == []
      assert apply(func, ([[1,2,3]],)) == [(1,),(2,),(3,)]
      assert apply(func, (["a", "b", "c", "d"],)) == [('a','b','c','d')]
      assert listeq(apply(func, ([[1,2,3], "ab"],)), 
                                        [(1,'a'),(1,'b'),
                                        (2,'a'),(2,'b'),
                                        (3,'a'),(3,'b')])
      assert apply(func, ([range(100), range(0)],)) == []
      assert listeq(apply(func, ([range(4), range(2), range(1), range(2)],)),
          [(0, 0, 0, 0), (0, 0, 0, 1), (0, 1, 0, 0), (0, 1, 0, 1),
           (1, 0, 0, 0), (1, 0, 0, 1), (1, 1, 0, 0), (1, 1, 0, 1),
           (2, 0, 0, 0), (2, 0, 0, 1), (2, 1, 0, 0), (2, 1, 0, 1),
           (3, 0, 0, 0), (3, 0, 0, 1), (3, 1, 0, 0), (3, 1, 0, 1)])
    except:
      print 'Correctness test FAILED for %s' % func.__name__
      return
    print 'Correctness test PASSED for %s' % func.__name__

  for func in funcs:
    ctest(func)
