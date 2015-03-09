from itertools import combinations
import random
import math
import copy


def euclid(a, b):
    """returns the Greatest Common Divisor of a and b"""
    a = abs(a)
    b = abs(b)
    if a < b:
        a, b = b, a
    while b != 0:
        a, b = b, a % b
    return a


def co_prime(l):
    """returns 'True' if the values in the list L are all co-prime
       otherwise, it returns 'False'. """
    for i, j in combinations(l, 2):
        if euclid(i, j) != 1:
            return False
    return True


def extended_euclid(a, b):
    """return a tuple of three values: x, y and z, such that x is
    the GCD of a and b, and x = y * a + z * b"""
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = extended_euclid(b % a, a)
        return g, x - (b // a) * y, y


def modulo_inverse(a, m):
    """returns the multiplicative inverse of a in modulo m as a
       positive value between zero and m-1"""
    # notice that a and m need to co-prime to each other.
    if co_prime([a, m]):
        linear_combination = extended_euclid(a, m)
        return linear_combination[1] % m
    else:
        return 0


def extract_twos(m):
    """m is a positive integer. A tuple (s, d) of integers is returned
    such that m = (2 ** s) * d."""
    # the problem can be break down to count how many '0's are there in
    # the end of bin(m). This can be done this way: m & a stretch of '1's
    # which can be represent as (2 ** n) - 1.
    assert m >= 0
    i = 0
    while m & (2 ** i) == 0:
        i += 1
    return i, m >> i


def int_to_base_two_list(x):
    """x is a positive integer. Convert it to base two as a list of integers
    in reverse order as a list."""
    # repeating x >>= 1 and x & 1 will do the trick
    assert x >= 0
    bit_inverse = []
    while x != 0:
        bit_inverse.append(x & 1)
        x >>= 1
    return bit_inverse


def modulo_exp(a, d, n):
    """returns a ** d (mod n)"""
    assert d >= 0
    assert n >= 0
    base2_array = int_to_base_two_list(d)
    base2_array_len = len(base2_array)
    modulo_array = []
    result = 1
    for i in range(1, base2_array_len + 1):
        if i == 1:
            modulo_array.append(a % n)
        else:
            modulo_array.append((modulo_array[i - 2] ** 2) % n)
    for i in range(0, base2_array_len):
        if base2_array[i] == 1:
            result *= base2_array[i] * modulo_array[i]
    return result % n


def miller_rabin(n, k):
    """
    Miller Rabin pseudo-prime test
    return True means likely a prime, (how sure about that, depending on k)
    return False means definitely a composite.
    Raise assertion error when n, k are not positive integers
    and n is not 1
    """
    assert n >= 1
    # ensure n is bigger than 1
    assert k > 0
    # ensure k is a positive integer so everything down here makes sense

    if n == 2:
        return True
    # make sure to return True if n == 2

    if n % 2 == 0:
        return False
    # immediately return False for all the even numbers bigger than 2

    extract2 = extract_twos(n - 1)
    s = extract2[0]
    d = extract2[1]
    assert 2 ** s * d == n - 1

    def check_for_composition(a):
        """Inner function which will inspect whether a given witness
        will reveal the true identity of n. Will only be called within
        miller_rabin"""
        x = modulo_exp(a, d, n)
        if x == 1 or x == n - 1:
            return None
        else:
            for j in range(1, s):
                x = modulo_exp(x, 2, n)
                if x == 1:
                    return False
                elif x == n - 1:
                    return None
            return False

    for i in range(0, k):
        a = random.randint(2, n - 2)
        if check_for_composition(a) == False:
            return False
    return True  # actually, we should return probably true.


def find_prime(a, b, k):
    """Return a pseudo prime number roughly between a and b,
    (could be larger than b). Raise ValueError if cannot find a
    pseudo prime after 10 * ln(x) + 3 tries. """
    x = random.randint(a, b)
    for i in range(0, int(10 * math.log(x) + 3)):
        if miller_rabin(x, k):
            return x
        else:
            x += 1
    raise ValueError


def calculate_new_key(a, b, k):
    """ Try to find two large pseudo primes roughly between a and b.
    Generate public and private keys for RSA encryption.
    Raises ValueError if it fails to find one"""
    try:
        p = find_prime(a, b, k)
        while True:
            q = find_prime(a, b, k)
            if q != p:
                break
    except:
        raise ValueError
    n = p * q
    m = (p - 1) * (q - 1)
    while True:
        e = random.randint(1, m)
        if co_prime([e, m]):
            break
    d = modulo_inverse(e, m)
    return (n, e, d)


def string_to_numbers_list(strn):
    """Converts a string to a list of integers based on ASCII values"""
    # Note that ASCII printable characters range is 0x20 - 0x7E
    return [ord(chars) for chars in strn]


def numbers_list_to_string(l):
    """Converts a list of integers to a string based on ASCII values"""
    # Note that ASCII printable characters range is 0x20 - 0x7E
    return ''.join(map(chr, l))


def numbers_list_to_blocks(l, n):
    """Take a list of integers(each between 0 and 127), and combines them
    into block size n using base 256. If len(L) % n != 0, use some random
    junk to fill L to make it."""
    # Note that ASCII printable characters range is 0x20 - 0x7E
    result_list = []
    to_process = copy.copy(l)
    if len(to_process) % n != 0:
        for i in range(0, n - len(to_process) % n):
            to_process.append(random.randint(32, 126))
            # to_process.append(0)
    for i in range(0, len(to_process), n):
        block = 0
        for j in range(0, n):
            block += to_process[i + j] << (8 * (n - j - 1))
        result_list.append(block)
    return result_list


def blocks_to_numbers_list(blocks, n):
    """inverse function of numbers_list_to_blocks."""
    to_process = copy.copy(blocks)
    result_list = []
    for numbers_block in to_process:
        inner = []
        for i in range(0, n):
            inner.append(numbers_block % 256)
            numbers_block >>= 8
        inner.reverse()
        result_list.extend(inner)
    return result_list


def encrypt(message, modN, e, block_size):
    """given a string message, public keys and block_size, encrypt using
    RSA algorithms."""
    numList = string_to_numbers_list(message)
    numbers_blocks = numbers_list_to_blocks(numList, block_size)
    return [modulo_exp(blocks, e, modN) for blocks in numbers_blocks]


def decrypt(secret, modN, d, block_size):
    """reverse function of encrypt"""
    numbers_blocks = [modulo_exp(blocks, d, modN) for blocks in secret]
    numList = blocks_to_numbers_list(numbers_blocks, block_size)
    return numbers_list_to_string(numList)

if __name__ == '__main__':
    (n, e, d) = calculate_new_key(10 ** 100, 10 ** 101, 50)
    print'Enter the text to be encrypted: '
    message = raw_input()
    print ('n = {0}'.format(n))
    print ('e = {0}'.format(e))
    print ('d = {0}'.format(d))
    print(message)
    cipher = encrypt(message, n, e, 15)
    print(cipher)
    deciphered = decrypt(cipher, n, d, 15)
    print(deciphered)
