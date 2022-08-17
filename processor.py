from enum import Enum
import random

class processor:
    class Instruction(Enum):
        i_add        = 1
        i_sub        = 2
        i_xor        = 3
        i_and        = 4
        i_or         = 5
        i_load       = 6
        i_shift_r    = 8
        i_rot_circ_r = 9

    class SourceType(Enum):
        st_reg = 1
        st_val = 2
        # st_ind = 3  TODO

    class DestinationType(Enum):
        dt_reg = 1

    masks = { 8: 255, 16: 65535 }

    def __init__(self):
        pass

    # allocate them
    def init_registers(self):
        assert False

    # set them to initial values
    def reset_registers(self, initial_values):
        self.init_registers()

        for iv in initial_values:
            reg_found = False

            for r in self.registers:
                if self.registers[r]['width'] == iv['width'] and self.registers[r]['set'] == False:
                    self.registers[r]['value']  = iv['value']
                    self.registers[r]['ivalue'] = iv['value']

                    self.registers[r]['set']    = True

                    reg_found = True
                    break

            assert reg_found == True

    def generate_program(self, max_length):
        instruction_count = random.randint(1, max_length)

        program = []

        for nr in range(0, instruction_count):
            program.append(self.pick_an_instruction())

        return program

    def pick_a_register(self, width, can_be_destination):
        while True:
            register = random.choice(list(self.registers))

            if self.registers[register]['width'] == width or width == None:
                if can_be_destination == True:
                    if self.registers[register]['dest_allowed'] == True:
                        return register

                else:
                    return register

    def insert_program_init(self):
        assert False

    def pick_an_instruction(self):
        assert False

    def reset_ram(self):
        self.ram = [ 0 ] * self.ram_size

    def get_accumulator(self):
        assert False

    def get_register_value(self, reg_name):
        is_pair = 'pair' in self.registers[reg_name]

        if is_pair:
            value = 0

            for dest in self.registers[reg_name]['pair']:
                value |= self.registers[dest]['value']
                value <<= 8

            return value

        else:
            return self.registers[reg_name]['value']

    def set_register_value(self, reg_name, value):
        assert value != None

        is_pair = 'pair' in self.registers[reg_name]

        if is_pair:
            for dest in reversed(self.registers[reg_name]['pair']):
                self.registers[dest]['value'] = value & 255
                value >>= 8

        else:
            self.registers[reg_name]['value'] = value

    def execute_program(self, initial_values, program):
        self.reset_registers(initial_values)

        self.reset_ram()

        for instruction in program:
            if instruction['instruction'] in [ processor.Instruction.i_add, processor.Instruction.i_sub, processor.Instruction.i_xor, processor.Instruction.i_and, processor.Instruction.i_or ]:
                work_value = 0

                for source in instruction['sources']:
                    cur_value = None

                    if source['type'] == processor.SourceType.st_reg:
                        cur_value = self.get_register_value(source['name'])

                    elif source['type'] == processor.SourceType.st_val:
                        cur_value = source['value']

                    else:
                        assert False

                    if work_value == None:
                        work_value = cur_value

                    elif instruction['instruction'] == processor.Instruction.i_add:
                        work_value += cur_value

                    elif instruction['instruction'] == processor.Instruction.i_sub:
                        work_value -= cur_value

                    elif instruction['instruction'] == processor.Instruction.i_xor:
                        work_value ^= cur_value

                    elif instruction['instruction'] == processor.Instruction.i_and:
                        work_value &= cur_value

                    elif instruction['instruction'] == processor.Instruction.i_or:
                        work_value |= cur_value

                    else:
                        assert False

                if instruction['destination']['type'] == processor.DestinationType.dt_reg:
                    self.set_register_value(instruction['destination']['name'], work_value)

                else:
                    assert False

            elif instruction['instruction'] == processor.Instruction.i_load:
                work_value = None

                # load should have only one
                for source in instruction['sources']:
                    cur_value = None

                    if source['type'] == processor.SourceType.st_reg:
                        cur_value = self.get_register_value(source['name'])

                    elif source['type'] == processor.SourceType.st_val:
                        cur_value = source['value']

                    else:
                        assert False

                    assert work_value == None

                    work_value = cur_value

                assert work_value != None

                if instruction['destination']['type'] == processor.DestinationType.dt_reg:
                    self.set_register_value(instruction['destination']['name'], work_value)

                else:
                    assert False

            elif instruction['instruction'] == processor.Instruction.i_shift_r:
                work_value = self.get_register_value(instruction['destination']['name'])

                work_value >>= instruction['shift_n']

                self.set_register_value(instruction['destination']['name'], work_value)

            elif instruction['instruction'] == processor.Instruction.i_rot_circ_r:
                work_value = self.get_register_value(instruction['destination']['name'])

                old_0 = work_value & 1

                work_value >>= instruction['shift_n']

                work_value |= old_0 << (self.registers[instruction['destination']['name']]['width'] - 1)

                self.set_register_value(instruction['destination']['name'], work_value)

            elif instruction['instruction'] == processor.Instruction.i_rot_circ_l:
                work_value = self.get_register_value(instruction['destination']['name'])

                old_7 = 1 if work_value & 128 else 0

                work_value <<= instruction['shift_n']

                work_value &= processor.masks[self.registers[instruction['destination']['name']]['width']]

                work_value |= old_7

                self.set_register_value(instruction['destination']['name'], work_value)

            else:
                assert False
