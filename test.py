#! /usr/bin/python3

from processor_z80 import processor_z80


initialize_with = [ { 'width' : 8, 'value' : 123 },
                    { 'width' : 8, 'value' : 9 } ]

p = processor_z80(initialize_with)

print(p.pick_operation())
