import time
import math

def isprime(n):
    """Returns True if n is prime and False otherwise"""
    if not isinstance(n, int):
        raise TypeError("argument passed to is_prime is not of 'int' type")
    if n < 2:
        return False
    if n == 2:
        return True
    max = int(math.ceil(math.sqrt(n)))
    i = 2
    while i <= max:
        if n % i == 0:
            return False
        i += 1
    return True

def sum_primes(n):
    """Calculates sum of all primes below given integer n"""
    return sum([x for x in xrange(2,n) if isprime(x)])


start_time = time.time()

inputs = xrange(100000, 1000000, 10000)
for x in inputs:
    print "%d: %d" % (x, sum_primes(x))

print "Time elapsed: ", time.time() - start_time, "s"
