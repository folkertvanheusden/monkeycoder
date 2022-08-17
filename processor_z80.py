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
        self.registers['A'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['B'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['C'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['D'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['E'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['H'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['L'] = { 'width': 8, 'value': 0, 'ivalue' : None, 'set': False, 'dest_allowed': True }
        self.registers['HL'] = { 'width': 16, 'value': 0, 'ivalue' : None, 'set': False, 'pair': ['H', 'L'], 'dest_allowed': True }
        self.registers['BC'] = { 'width': 16, 'value': 0, 'ivalue' : None, 'set': False, 'pair': ['B', 'C'], 'dest_allowed': False }
        self.registers['DE'] = { 'width': 16, 'value': 0, 'ivalue' : None, 'set': False, 'pair': ['D', 'E'], 'dest_allowed': False }

    def insert_program_init(self, dest, initial_values):
        self.reset_registers(initial_values)

        for register in self.registers:
            v = self.registers[register]['ivalue']
            if v == None:
                v = 0

            instruction = dict()
            instruction['instruction'] = processor.Instruction.i_load
            instruction['sources']     = [ { 'type': processor.SourceType.st_val, 'value': 0 } ]
            instruction['destination'] = dict()
            instruction['destination']['type'] = processor.DestinationType.dt_reg
            instruction['destination']['name'] = register
            instruction['opcode'] = f"LD {instruction['destination']['name']}, {v}"

            dest.insert(0, instruction)

    def pick_an_instruction(self):
        instr_type = random.randint(0, 1)

        instruction = dict()

        if instr_type == 0:
            sub_type = random.choice([ processor.Instruction.i_add, processor.Instruction.i_sub, processor.Instruction.i_xor, processor.Instruction.i_and, processor.Instruction.i_or ])

            instruction['instruction'] = sub_type

            width = random.choice([8, 16]) if sub_type == processor.Instruction.i_add else 8

            source = { 'type': processor.SourceType.st_reg, 'name': self.pick_a_register(width, None) } if random.choice([True, False]) or width == 16 else { 'type': processor.SourceType.st_val, 'value': random.randint(0, 255) }
            instruction['sources']     = [ source ]

            instruction['destination'] = dict()
            instruction['destination']['type'] = processor.DestinationType.dt_reg
            instruction['destination']['name'] = 'A' if width == 8 else 'HL'

            if source['type'] == processor.SourceType.st_reg:
                instruction['opcode'] = f"{self.instr_mapping[sub_type]} {instruction['destination']['name']}, {source['name']}"
            
            elif source['type'] == processor.SourceType.st_val:
                instruction['opcode'] = f"{self.instr_mapping[sub_type]} {instruction['destination']['name']}, ${source['value']:02X}"

            else:
                assert False

        elif instr_type == 1:
            instruction['instruction'] = processor.Instruction.i_load

            instruction['destination'] = dict()
            instruction['destination']['type'] = processor.DestinationType.dt_reg
            instruction['destination']['name'] = self.pick_a_register(8, True)

            if random.randint(0, 1) == 0:
                register = self.pick_a_register(8, True)

                instruction['sources'] = [ { 'type': processor.SourceType.st_reg, 'name': register } ]
                instruction['opcode'] = f"LD {instruction['destination']['name']}, {register}"

            else:
                v = random.randint(0, 255)
                instruction['sources'] = [ { 'type': processor.SourceType.st_val, 'value': v } ]
                instruction['opcode'] = f"LD {instruction['destination']['name']}, {v}"

        else:
            assert False

        return instruction

    def get_accumulator(self):
        return self.get_register_value('A')
