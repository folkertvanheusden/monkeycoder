from processor import processor
import random

class processor_z80(processor):
    def __init__(self, init_registers_with):
        self.operations = dict()
        self.operations['add'] = dict()
        self.operations['add']['generate'] = self.operation_add_sub
        self.operations['add']['targets' ] = [ { 'name': 'A', 'width': 8 },
                                               { 'name': 'HL', 'width': 16 },
                                             ]
        self.operations['add']['sources' ] = [ { 'name': 'A', 'width': 8 },
                                               { 'name': 'B', 'width': 8 },
                                               { 'name': 'C', 'width': 8 },
                                               { 'name': 'D', 'width': 8 },
                                               { 'name': 'E', 'width': 8 },
                                               { 'name': 'H', 'width': 8 },
                                               { 'name': 'L', 'width': 8 },
                                             ]

        self.ram_size = 65536

        super().__init__(init_registers_with)

    def init_registers(self):
        self.registers = dict()
        # affects == None: affects itself, else it means a register is in reality a pair
        self.registers['A'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['B'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['C'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['D'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['E'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['H'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['L'] = { 'width': 8, 'affects': None, 'in_use': False, 'value': 0 }
        self.registers['BC'] = { 'width': 16, 'affects': ['B', 'C'], 'in_use': False, 'value': 0 }
        self.registers['DE'] = { 'width': 16, 'affects': ['D', 'E'], 'in_use': False, 'value': 0 }
        self.registers['HL'] = { 'width': 16, 'affects': ['H', 'L'], 'in_use': False, 'value': 0 }

        # affects in order of MSB to LSB
        self.indirect = dict()
        self.indirect['(HL)'] = { 'width': 16, 'affects': ['H', 'L'] }

    def get_accumulator(self):
        return 'A'

    def invoke_add_sub(self, reg_dst, instruction_choice, value):
            if instruction_choice == 'ADD':
                reg_dst[1]['value'] += value

            elif instruction_choice == 'SUB':
                reg_dst[1]['value'] -= value

            else:
                assert False

            reg_dst[1]['value'] &= 255

    def operation_add_sub(self):
        operation = None

        instruction_choice = random.choice(['ADD', 'SUB'])

        instr_type_choice = random.randint(0, 2)

        if instr_type_choice == 0:
            reg_dst = self.allocate_register('A')
            reg_src = self.allocate_random_register(8)

            operation = { 'name': f'{instruction_choice} {reg_dst[0]}, {reg_src[0]}' }

            self.invoke_add_sub(reg_dst, instruction_choice, reg_src[1]['value'])

            self.free_register(reg_src[0])
            self.free_register('A')

        elif instr_type_choice == 1:
            reg_dst = self.allocate_register('A')
            ind_src = self.allocate_random_indirect(16)

            operation = { 'name': f'{instruction_choice} {reg_dst[0]}, {ind_src[0]}' }

            value = self.get_register_pair_16(ind_src[1]['affects'][0], ind_src[1]['affects'][1])

            self.invoke_add_sub(reg_dst, instruction_choice, value)

            self.free_indirect(ind_src[0])
            self.free_register('A')

        elif instr_type_choice == 2:
            reg_dst = self.allocate_register('A')
            val_src = random.randint(0, 255)

            operation = { 'name': f'{instruction_choice} {reg_dst[0]}, ${val_src:02x}' }

            self.invoke_add_sub(reg_dst, instruction_choice, val_src)

            self.free_register('A')

        else:
            assert False

        return operation
