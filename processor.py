from enum import Enum
import random

class processor:
    class Instruction(Enum):
        i_add  = 1
        i_sub  = 2
        i_xor  = 3
        i_and  = 4
        i_or   = 5
        i_load = 6

    class SourceType(Enum):
        st_reg = 1
        st_val = 2
        # st_ind = 3  TODO

    class DestinationType(Enum):
        dt_reg = 1

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

    def pick_a_register(self):
        return random.choice(list(self.registers))

    def insert_program_init(self):
        assert False

    def pick_an_instruction(self):
        assert False

    def reset_ram(self):
        self.ram = [ 0 ] * self.ram_size

    def get_accumulator(self):
        assert False

    def get_register_value(self, reg_name):
        return self.registers[reg_name]['value']

    def set_register_value(self, reg_name, value):
        assert value != None

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

            else:
                assert False
