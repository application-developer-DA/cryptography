from __future__ import division
from heapq import heappush, heappop, heapify
from collections import defaultdict
from math import log

def build_tree(symbols_weights):
    heap = [ (weight, symbol) for symbol, weight in symbols_weights.items() ]
    heapify(heap)
    while len(heap) > 1:
        lweight, lsymbol = heappop(heap)
        rweight, rsymbol = heappop(heap)
        heappush(heap, (lweight + rweight, (lsymbol, rsymbol)))
    tree = heappop(heap)
    return tree

def calculate_codes(node, code = ""):
    if type(node) is not tuple:
        return [(node, code)]

    if type(node[0]) is int: # if it is a root
        l, r = node[1]
    else:
        l, r = node

    return calculate_codes(l, code + "0") + calculate_codes(r, code + "1")

# TODO: make better
def decode(tree, encoded_text):
    pos = tree
    for bit in encoded_text:
        if bit == 0:
            pos = pos[1][0]
        else:
            pos = pos[1][1]
        if type(pos[1]) is not tuple: # we get into the leaf
            pos = tree

def decode2(encoded_text, table):
    return [key for key, value in table.items() if value == encoded_text][0]

if __name__ == "__main__":
    input_str = raw_input("Enter the text to be encoded: ")
    symbols_weights = defaultdict(int)
    for char in input_str:
        symbols_weights[char] += 1

    tree = build_tree(symbols_weights)
    huffman_table = dict(calculate_codes(tree))

    print "Huffman code table:"
    print "Symbol\tWeight\tCode"
    for symbol in huffman_table:
        print "%s\t%s\t%s" % (symbol, symbols_weights[symbol], huffman_table[symbol])

    print "Initial text:", "".join( [bin(ord(x)) for x in input_str] ).replace("0b", "")
    print "Encoded text:", "".join([ huffman_table[c] for c in input_str ])
    print "Decoded text:", "".join([ decode2(huffman_table[c], huffman_table) for c in input_str ])

    probabilities = [ x/sum(symbols_weights.values()) for x in symbols_weights.values() ]
    print sum(probabilities)
    entropy = -sum([ probability * log(probability, 2) for probability in probabilities ])

    probabilities_dict = { sym: probability for sym, probability in zip(symbols_weights.keys(), probabilities) }
    cost = sum([ probabilities_dict[symbol] * len(huffman_table[symbol]) for symbol in huffman_table ])

    redundancy = cost - entropy

    print "Entropy: %f" % (entropy)
    print "Cost: %f" % (cost)
    print "Redundancy: %f" % (redundancy)
