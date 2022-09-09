from enum import Enum
from random import SystemRandom
from typing import Callable, List, Optional, Tuple, TypedDict

rng = SystemRandom()

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

    class registers_dict(TypedDict):
        width : int
        value : int
        ivalue: int
        name  : str
        set_  : bool

    masks = { 8: 255, 16: 65535 }

    def __init__(self) -> None:
        self.registers: processor.registers_dict = { }
        self.ram_size: int   = 0

    # allocate them
    def init_registers(self) -> None:
        assert False

    # set them to initial values
    def reset_registers(self, initial_values: dict) -> None:
        self.init_registers()

        for iv in initial_values:
            reg_found: bool = False

            for r in self.registers:
                if self.registers[r]['width'] == iv['width'] and self.registers[r]['set_'] == False:
                    self.registers[r]['value']  = iv['value']
                    self.registers[r]['ivalue'] = iv['value']

                    self.registers[r]['set_']    = True

                    reg_found = True
                    break

            assert reg_found == True

    def generate_program(self, max_length: int) -> list[dict]:
        instruction_count: int = rng.randint(1, max_length)

        program: list[dict] = []

        for nr in range(0, instruction_count):
            program.append(self.pick_an_instruction())

        return program

    def pick_a_register(self, width: int, can_be_destination: Optional[bool]) -> dict:
        while True:
            register = rng.choice(list(self.registers))

            if self.registers[register]['width'] == width or width == None:
                if can_be_destination == True:
                    if self.registers[register]['dest_allowed'] == True:
                        return register

                else:
                    return register

    def get_program_init(self, initial_values: dict) -> List[dict]:
        assert False

    def pick_an_instruction(self) -> dict:
        assert False

    def reset_ram(self) -> None:
        # self.ram = [ 0 ] * self.ram_size  TODO
        pass

    def get_accumulator(self) -> int:
        assert False

    def get_register_value(self, reg_name: str) -> int:
        is_pair = 'pair' in self.registers[reg_name]

        if is_pair:
            value = 0

            for dest in self.registers[reg_name]['pair']:
                cur_byte = self.registers[dest]['value']

                assert cur_byte != None
                assert cur_byte >= 0
                assert cur_byte < 256

                value <<= 8
                value |= cur_byte

            return value

        else:
            cur_byte = self.registers[reg_name]['value']

            assert cur_byte != None
            assert cur_byte >= 0
            assert cur_byte < 256

            return cur_byte

    def set_register_value(self, reg_name: str, value: int) -> None:
        assert value != None

        is_pair = 'pair' in self.registers[reg_name]

        if is_pair:
            assert value >= 0

            for dest in reversed(self.registers[reg_name]['pair']):
                self.registers[dest]['value'] = value & 255
                value >>= 8

            assert value == 0

        else:
            assert value >= 0
            assert value < 256

            self.registers[reg_name]['value'] = value

    def execute_program(self, initial_values: dict, program: dict) -> None:
        self.reset_registers(initial_values)

        self.reset_ram()

        for instruction in program:
            if instruction['instruction'] in [ processor.Instruction.i_add, processor.Instruction.i_sub, processor.Instruction.i_xor, processor.Instruction.i_and, processor.Instruction.i_or ]:
                work_value:  int  = -1
                first_value: bool = True

                for source in instruction['sources']:
                    cur_value: int = -1

                    if source['type'] == processor.SourceType.st_reg:
                        cur_value = self.get_register_value(source['name'])

                    elif source['type'] == processor.SourceType.st_val:
                        cur_value = source['value']

                    else:
                        assert False

                    assert cur_value != None
                    assert cur_value >= 0

                    if first_value == True:
                        first_value = False

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

                assert first_value == False

                if instruction['destination']['type'] == processor.DestinationType.dt_reg:
                    mask = processor.masks[self.registers[instruction['destination']['name']]['width']]

                    work_value &= mask

                    self.set_register_value(instruction['destination']['name'], work_value)

                else:
                    assert False

            elif instruction['instruction'] == processor.Instruction.i_load:
                # load should have only one source
                assert len(instruction['sources']) == 1

                source = instruction['sources'][0]

                if source['type'] == processor.SourceType.st_reg:
                    work_value = self.get_register_value(source['name'])

                elif source['type'] == processor.SourceType.st_val:
                    work_value = source['value']

                else:
                    assert False

                if instruction['destination']['type'] == processor.DestinationType.dt_reg:
                    self.set_register_value(instruction['destination']['name'], work_value)

                else:
                    assert False

            elif instruction['instruction'] == processor.Instruction.i_shift_r:
                register = instruction['destination']['name']

                work_value = self.get_register_value(register)

                work_value >>= instruction['shift_n']

                self.set_register_value(register, work_value)

            elif instruction['instruction'] == processor.Instruction.i_rot_circ_r:
                register = instruction['destination']['name']

                work_value = self.get_register_value(register)

                bit_shift_n = self.registers[register]['width'] - 1

                for i in range(0, instruction['shift_n']):
                    old_0 = work_value & 1

                    work_value >>= 1

                    work_value |= old_0 << bit_shift_n

                self.set_register_value(register, work_value)

            elif instruction['instruction'] == processor.Instruction.i_rot_circ_l:
                register = instruction['destination']['name']

                work_value = self.get_register_value(register)

                mask = processor.masks[self.registers[register]['width']]

                for i in range(0, instruction['shift_n']):
                    old_7 = 1 if work_value & 128 else 0

                    work_value <<= 1

                    work_value &= mask

                    work_value |= old_7

                self.set_register_value(register, work_value)

            else:
                assert False
