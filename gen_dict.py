import binascii

hex_strings = [
    'e5b7a5e58fb7',
    'e5a793e5908d',
    'e8bda6e997b4',
    'e581a5e5bab7e8af81e78ab6e680812fe69c89e69588e69c9f',
    'e4b88ae5b297e8af81e78ab6e680812fe69c89e69588e69c9f',
    'e68a80e883bde79fa9e998b5'
]
mapping = { binascii.unhexlify(h).decode('utf-8'): "unknown" for h in hex_strings }
print(repr(mapping))
