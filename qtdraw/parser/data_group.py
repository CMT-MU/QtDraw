"""
Group data.

This module contains data for space group info.
"""

# ==================================================
_shift_vectors = {  # shift vector for origin choice 2.
    48: [-0.25, -0.25, -0.25],
    50: [-0.25, -0.25, 0.0],
    59: [-0.25, -0.25, 0.0],
    68: [0.0, -0.25, -0.25],
    70: [0.125, 0.125, 0.125],
    85: [0.25, -0.25, 0.0],
    86: [0.25, 0.25, 0.25],
    88: [0.0, 0.25, 0.125],
    125: [0.25, 0.25, 0.0],
    126: [0.25, 0.25, 0.25],
    129: [0.25, -0.25, 0.0],
    130: [0.25, -0.25, 0.0],
    133: [0.25, -0.25, 0.25],
    134: [0.25, -0.25, 0.25],
    137: [0.25, -0.25, 0.25],
    138: [0.25, -0.25, 0.25],
    141: [0.0, -0.25, 0.125],
    142: [0.0, -0.25, 0.125],
    201: [0.25, 0.25, 0.25],
    203: [0.125, 0.125, 0.125],
    222: [0.25, 0.25, 0.25],
    224: [0.25, 0.25, 0.25],
    227: [0.125, 0.125, 0.125],
    228: [0.375, 0.375, 0.375],
}


# ==================================================
_data_no_space_group = {  # no - space_group map, {int : str}.
    1: "C1^1",
    2: "Ci^1",
    3: "C2^1",
    4: "C2^2",
    5: "C2^3",
    6: "Cs^1",
    7: "Cs^2",
    8: "Cs^3",
    9: "Cs^4",
    10: "C2h^1",
    11: "C2h^2",
    12: "C2h^3",
    13: "C2h^4",
    14: "C2h^5",
    15: "C2h^6",
    16: "D2^1",
    17: "D2^2",
    18: "D2^3",
    19: "D2^4",
    20: "D2^5",
    21: "D2^6",
    22: "D2^7",
    23: "D2^8",
    24: "D2^9",
    25: "C2v^1",
    26: "C2v^2",
    27: "C2v^3",
    28: "C2v^4",
    29: "C2v^5",
    30: "C2v^6",
    31: "C2v^7",
    32: "C2v^8",
    33: "C2v^9",
    34: "C2v^10",
    35: "C2v^11",
    36: "C2v^12",
    37: "C2v^13",
    38: "C2v^14",
    39: "C2v^15",
    40: "C2v^16",
    41: "C2v^17",
    42: "C2v^18",
    43: "C2v^19",
    44: "C2v^20",
    45: "C2v^21",
    46: "C2v^22",
    47: "D2h^1",
    48: "D2h^2",
    49: "D2h^3",
    50: "D2h^4",
    51: "D2h^5",
    52: "D2h^6",
    53: "D2h^7",
    54: "D2h^8",
    55: "D2h^9",
    56: "D2h^10",
    57: "D2h^11",
    58: "D2h^12",
    59: "D2h^13",
    60: "D2h^14",
    61: "D2h^15",
    62: "D2h^16",
    63: "D2h^17",
    64: "D2h^18",
    65: "D2h^19",
    66: "D2h^20",
    67: "D2h^21",
    68: "D2h^22",
    69: "D2h^23",
    70: "D2h^24",
    71: "D2h^25",
    72: "D2h^26",
    73: "D2h^27",
    74: "D2h^28",
    75: "C4^1",
    76: "C4^2",
    77: "C4^3",
    78: "C4^4",
    79: "C4^5",
    80: "C4^6",
    81: "S4^1",
    82: "S4^2",
    83: "C4h^1",
    84: "C4h^2",
    85: "C4h^3",
    86: "C4h^4",
    87: "C4h^5",
    88: "C4h^6",
    89: "D4^1",
    90: "D4^2",
    91: "D4^3",
    92: "D4^4",
    93: "D4^5",
    94: "D4^6",
    95: "D4^7",
    96: "D4^8",
    97: "D4^9",
    98: "D4^10",
    99: "C4v^1",
    100: "C4v^2",
    101: "C4v^3",
    102: "C4v^4",
    103: "C4v^5",
    104: "C4v^6",
    105: "C4v^7",
    106: "C4v^8",
    107: "C4v^9",
    108: "C4v^10",
    109: "C4v^11",
    110: "C4v^12",
    111: "D2d^1",
    112: "D2d^2",
    113: "D2d^3",
    114: "D2d^4",
    115: "D2d^5",
    116: "D2d^6",
    117: "D2d^7",
    118: "D2d^8",
    119: "D2d^9",
    120: "D2d^10",
    121: "D2d^11",
    122: "D2d^12",
    123: "D4h^1",
    124: "D4h^2",
    125: "D4h^3",
    126: "D4h^4",
    127: "D4h^5",
    128: "D4h^6",
    129: "D4h^7",
    130: "D4h^8",
    131: "D4h^9",
    132: "D4h^10",
    133: "D4h^11",
    134: "D4h^12",
    135: "D4h^13",
    136: "D4h^14",
    137: "D4h^15",
    138: "D4h^16",
    139: "D4h^17",
    140: "D4h^18",
    141: "D4h^19",
    142: "D4h^20",
    143: "C3^1",
    144: "C3^2",
    145: "C3^3",
    146: "C3^4",
    147: "C3i^1",
    148: "C3i^2",
    149: "D3^1",
    150: "D3^2",
    151: "D3^3",
    152: "D3^4",
    153: "D3^5",
    154: "D3^6",
    155: "D3^7",
    156: "C3v^1",
    157: "C3v^2",
    158: "C3v^3",
    159: "C3v^4",
    160: "C3v^5",
    161: "C3v^6",
    162: "D3d^1",
    163: "D3d^2",
    164: "D3d^3",
    165: "D3d^4",
    166: "D3d^5",
    167: "D3d^6",
    168: "C6^1",
    169: "C6^2",
    170: "C6^3",
    171: "C6^4",
    172: "C6^5",
    173: "C6^6",
    174: "C3h^1",
    175: "C6h^1",
    176: "C6h^2",
    177: "D6^1",
    178: "D6^2",
    179: "D6^3",
    180: "D6^4",
    181: "D6^5",
    182: "D6^6",
    183: "C6v^1",
    184: "C6v^2",
    185: "C6v^3",
    186: "C6v^4",
    187: "D3h^1",
    188: "D3h^2",
    189: "D3h^3",
    190: "D3h^4",
    191: "D6h^1",
    192: "D6h^2",
    193: "D6h^3",
    194: "D6h^4",
    195: "T^1",
    196: "T^2",
    197: "T^3",
    198: "T^4",
    199: "T^5",
    200: "Th^1",
    201: "Th^2",
    202: "Th^3",
    203: "Th^4",
    204: "Th^5",
    205: "Th^6",
    206: "Th^7",
    207: "O^1",
    208: "O^2",
    209: "O^3",
    210: "O^4",
    211: "O^5",
    212: "O^6",
    213: "O^7",
    214: "O^8",
    215: "Td^1",
    216: "Td^2",
    217: "Td^3",
    218: "Td^4",
    219: "Td^5",
    220: "Td^6",
    221: "Oh^1",
    222: "Oh^2",
    223: "Oh^3",
    224: "Oh^4",
    225: "Oh^5",
    226: "Oh^6",
    227: "Oh^7",
    228: "Oh^8",
    229: "Oh^9",
    230: "Oh^10",
}