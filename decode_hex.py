import binascii

hex_strings = [
    'e8aea2e58d95e7bc96e58fb7',
    'e789a9e69699e7bc96e7a081',
    'e79baee6a087e695b0e9878f',
    'e8aea1e58892e5bc80e5a78b',
    'e8aea1e58892e7bb93e69d9f',
    'e78ab6e68081'
]
for h in hex_strings:
    print(binascii.unhexlify(h).decode('utf-8'))
