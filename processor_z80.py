from processor import processor
import random

class processor_z80(processor):
    def __init__(self):
        self.ram_size = 65536

        self.init_registers()

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
        instr = 0 #random.randint(0, 1)

        instruction = dict()

        if instr == 0:  # ADD
            instruction['instruction'] = processor.Instruction.i_add

            source = { 'type': processor.SourceType.st_reg, 'name': self.pick_a_register() } if random.choice([True, False]) else { 'type': processor.SourceType.st_val, 'value': random.randint(0, 255) }
            instruction['sources']     = [ source ]

            instruction['destination'] = dict()
            instruction['destination']['type'] = processor.DestinationType.dt_reg
            instruction['destination']['name'] = 'A'

            if source['type'] == processor.SourceType.st_reg:
                instruction['opcode'] = f"ADD {instruction['destination']}, {source['name']}"
            
            elif source['type'] == processor.SourceType.st_val:
                instruction['opcode'] = f"ADD {instruction['destination']}, ${source['value']:02X}"

            else:
                assert False

        else:
            assert False

        return instruction

    def get_accumulator(self):
        return self.get_register_value('A')
