"""
This file is part of Lab 4 (Hamming Codes), assessed coursework for the module
COMP70103 Statistical Information Theory. 

You should submit an updated version of this file, replacing the
NotImplementedError's with the correct implementation of each function. Do not
edit any other functions.

Follow further instructions in the attached .pdf and .ipynb files, available
through Scientia.
"""
from typing import Callable, Dict, List, Tuple, Union
import numpy as np
import numpy.random as rn
from itertools import product

alphabet = "abcdefghijklmnopqrstuvwxyz01234567890 .,\n"
digits = "0123456789"

def char2bits(char: chr) -> np.array:
    '''
    Given a character in the alphabet, returns a 8-bit numpy array of 0,1 which represents it
    '''
    num   = ord(char)
    if num >= 256:
        raise ValueError("Character not recognised.")
    bits = format(num, '#010b')
    bits  = [ int(b) for b in bits[2:] ]
    return np.array(bits)


def bits2char(bits) -> chr:
    '''
    Given a 7-bit numpy array of 0,1 or bool, returns the character it encodes
    '''
    bits  = ''.join(bits.astype(int).astype(str))
    num   =  int(bits, base = 2)
    return chr(num)


def text2bits(text: str) -> np.ndarray:
    '''
    Given a string, returns a numpy array of bool with the binary encoding of the text
    '''
    text = text.lower()
    text = [ t for t in text if t in alphabet ]
    bits = [ char2bits(c) for c in text ]
    return np.array(bits, dtype = bool).flatten()


def bits2text(bits: np.ndarray) -> str:
    '''
    Given a numpy array of bool or 0 and 1 (as int) which represents the
    binary encoding a text, return the text as a string
    '''
    if np.mod(len(bits), 8) != 0:
        raise ValueError("The length of the bit string must be a multiple of 8.")
    bits = bits.reshape(int(len(bits)/8), 8)
    chrs = [ bits2char(b) for b in bits ]
    return ''.join(chrs)



def parity_bit_positions(m):
    select_cols = 2**np.arange(m) - 1
    seq = np.arange(2**m - 1)
    return np.isin(seq, select_cols)
  
def binary_vec_to_dec(bin: np.array):
    return int(sum([2**i * e for i, e in enumerate(bin)]))

def parity_matrix(m : int) -> np.ndarray:
    """
    m : int
      The number of parity bits to use

    return : np.ndarray
      m-by-n parity check matrix
      where n = 2^m - 1
    """
    n = 2**m - 1
    row_vec = np.arange(m)
    col_vec = np.atleast_2d(np.arange(1,n + 1)).T
    H = col_vec >> row_vec & 1
    return (H.T).astype(int)

def hamming_generator(m : int) -> np.ndarray:
    """
    m : int
      The number of parity bits to use

    return : np.ndarray
      k-by-n generator matrix
    """
    parity_bit_mask = parity_bit_positions(m)
    G = np.zeros((2**m-1, m+1), dtype=int)
    H = parity_matrix(m)
    
    G[parity_bit_mask] = H.T[~parity_bit_mask].T
    G[~parity_bit_mask] = np.eye(m+1)
    
    return G.T


def hamming_encode(data : np.ndarray, m : int) -> np.ndarray:
    """
    data : np.ndarray
      array of shape (k,) with the block of bits to encode

    m : int
      The number of parity bits to use

    return : np.ndarray
      array of shape (n,) with the corresponding Hamming codeword
    """
    assert( data.shape[0] == 2**m - m - 1 )
    return (data @ hamming_generator(m) % 2).astype(int)


def hamming_decode(code : np.ndarray, m : int) -> np.ndarray:
    """
    code : np.ndarray
      Array of shape (n,) containing a Hamming codeword computed with m parity bits
    m : int
      Number of parity bits used when encoding

    return : np.ndarray
      Array of shape (k,) with the decoded and corrected data
    """
    assert(np.log2(len(code) + 1) == int(np.log2(len(code) + 1)) == m)
    H = parity_matrix(m)
    parity_bit_mask = parity_bit_positions(m)
    code = code.copy()

    syndrome = H @ code % 2
    error_position = binary_vec_to_dec(syndrome)
    print(code)
    
    # correct single-bit error
    if error_position:
        code[error_position - 1] ^= 1

    return code[~parity_bit_mask] # extract data bits


def decode_secret(msg : np.ndarray) -> str:
    """
    msg : np.ndarray
      One-dimensional array of binary integers

    return : str
      String with decoded text
    """
    m = np.nan  # <-- Your guess goes here

    raise NotImplementedError


def binary_symmetric_channel(data : np.ndarray, p : float) -> np.ndarray:
    """
    data : np.ndarray
      1-dimensional array containing a stream of bits
    p : float
      probability by which each bit is flipped

    return : np.ndarray
      data with a number of bits flipped
    """

    raise NotImplementedError


def decoder_accuracy(m : int, p : float) -> float:
    """
    m : int
      The number of parity bits in the Hamming code being tested
    p : float
      The probability of each bit being flipped

    return : float
      The probability of messages being correctly decoded with this
      Hamming code, using the noisy channel of probability p
    """

    raise NotImplementedError

