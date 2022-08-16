from processor import processor
import random

class processor_z80(processor):
    def __init__(self):
        self.ram_size = 65536

        self.init_registers()

        self.instr_mapping = dict()
        self.instr_mapping[processor.Instruction.i_add] = 'ADD'
        self.instr_mapping[processor.Instruction.i_sub] = 'SUB'
        self.instr_mapping[processor.Instruction.i_xor] = 'XOR'
        self.instr_mapping[processor.Instruction.i_and] = 'AND'
        self.instr_mapping[processor.Instruction.i_or ] = 'OR'

        super().__init__()

    def init_registers(self):
        self.registers = dict()
        self.registers['A'] = { 'width': 8, 'value': 0, 'set': False }
        self.registers['B'] = { 'width': 8, 'value': 0, 'set': False }
        self.registers['C'] = { 'width': 8, 'value': 0, 'set': False }
        self.registers['D'] = { 'width': 8, 'value': 0, 'set': False }
        self.registers['E'] = { 'width': 8, 'value': 0, 'set': False }
        self.registers['H'] = { 'width': 8, 'value': 0, 'set': False }
        self.registers['L'] = { 'width': 8, 'value': 0, 'set': False }

    def pick_an_instruction(self):
        instr_type = 0 #random.randint(0, 1)

        instruction = dict()

        if instr_type == 0:  # ADD
            sub_type = random.choice([ processor.Instruction.i_add, processor.Instruction.i_sub, processor.Instruction.i_xor, processor.Instruction.i_and, processor.Instruction.i_or ])

            instruction['instruction'] = sub_type

            source = { 'type': processor.SourceType.st_reg, 'name': self.pick_a_register() } if random.choice([True, False]) else { 'type': processor.SourceType.st_val, 'value': random.randint(0, 255) }
            instruction['sources']     = [ source ]

            instruction['destination'] = dict()
            instruction['destination']['type'] = processor.DestinationType.dt_reg
            instruction['destination']['name'] = 'A'


            if source['type'] == processor.SourceType.st_reg:
                instruction['opcode'] = f"{self.instr_mapping[sub_type]} {instruction['destination']['name']}, {source['name']}"
            
            elif source['type'] == processor.SourceType.st_val:
                instruction['opcode'] = f"{self.instr_mapping[sub_type]} {instruction['destination']['name']}, ${source['value']:02X}"

            else:
                assert False

        else:
            assert False

        return instruction

    def get_accumulator(self):
        return self.get_register_value('A')
