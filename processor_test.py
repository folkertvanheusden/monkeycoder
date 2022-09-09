from processor import processor
from processor_z80 import processor_z80
from random import SystemRandom
from typing import List

rng = SystemRandom()

class processor_test(processor_z80):
    def __init__(self):
        super().__init__()

        self.ram_size = 65536

        self.init_registers()

        self.instr_mapping: dict = {}
        self.instr_mapping[processor.Instruction.i_add       ] = 'ADD'
        self.instr_mapping[processor.Instruction.i_sub       ] = 'SUB'
        self.instr_mapping[processor.Instruction.i_xor       ] = 'XOR'
        self.instr_mapping[processor.Instruction.i_and       ] = 'AND'
        self.instr_mapping[processor.Instruction.i_or        ] = 'OR'
        self.instr_mapping[processor.Instruction.i_load      ] = 'LD'
        self.instr_mapping[processor.Instruction.i_shift_r   ] = 'SRL'
        self.instr_mapping[processor.Instruction.i_rot_circ_r] = 'RRC'

    def init_registers(self) -> None:
        self.registers: dict = {}
        self.registers['A'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'dest_allowed': True }
        self.registers['B'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'dest_allowed': True }
        self.registers['C'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'dest_allowed': True }
