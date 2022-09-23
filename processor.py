from enum import Enum
import random
from typing import Callable, List, Optional, Tuple, TypedDict

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
                if r == self.get_accumulator_name():  # TODO handle situations where the accumulator is required to be used because of number of available registers
                    continue

                if self.registers[r]['width'] == iv['width'] and self.registers[r]['set_'] == False:
                    self.registers[r]['value']  = iv['value']
                    self.registers[r]['ivalue'] = iv['value']

                    self.registers[r]['set_']    = True

                    reg_found = True
                    break

            assert reg_found == True

        self.flag_carry    = False
        self.flag_zero     = False
        self.flag_negative = False

    def generate_program(self, max_length: int) -> List[dict]:
        instruction_count: int = random.randint(1, max_length)

        program: list[dict] = []

        for nr in range(0, instruction_count):
            program.append(self.pick_an_instruction())

        return program

    def pick_a_register(self, width: int, can_be_destination: Optional[bool]) -> dict:
        while True:
            register = random.choice(list(self.registers))

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

    def get_accumulator_name(self) -> str:
        assert False

    def get_accumulator(self) -> int:
        return self.get_register_value(self.get_accumulator_name())

    def get_register_value(self, reg_name: str) -> int:
        is_pair = 'pair' in self.registers[reg_name]

        if is_pair:
            value = 0

            for dest in self.registers[reg_name]['pair']:
                cur_byte = self.registers[dest]['value']

                assert cur_byte != None
                assert cur_byte >= 0
                assert cur_byte <= self.masks[self.registers[reg_name]['width']]

                value <<= 8
                value |= cur_byte

            return value

        else:
            cur_byte = self.registers[reg_name]['value']

            assert cur_byte != None
            assert cur_byte >= 0
            assert cur_byte <= self.masks[self.registers[reg_name]['width']]

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

    def _set_flags_add(self, dest, dest_value, mask):
        assert False

    def _set_flags_sub(self, dest, dest_value, mask):
        assert False

    def _set_flags_logic(self, dest, dest_value, mask):
        assert False

    def execute_program(self, initial_values: dict, program: dict) -> None:
        self.reset_registers(initial_values)

        self.reset_ram()

        for instruction in program:
            if instruction['instruction'] in [ processor.Instruction.i_add, processor.Instruction.i_sub, processor.Instruction.i_xor, processor.Instruction.i_and, processor.Instruction.i_or ]:
                work_value:  int  = -1
                first_value: bool = True

                mask: Optional[int] = None

                if instruction['destination']['type'] == processor.DestinationType.dt_reg:
                    mask = processor.masks[self.registers[instruction['destination']['name']]['width']]

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

                if instruction['instruction'] == processor.Instruction.i_add:
                    self._set_flags_add(instruction['destination']['name'], work_value, mask)

                elif instruction['instruction'] == processor.Instruction.i_sub:
                    self._set_flags_sub(instruction['destination']['name'], work_value, mask)

                elif instruction['instruction'] == processor.Instruction.i_xor:
                    self._set_flags_logic(instruction['destination']['name'], work_value, mask)

                elif instruction['instruction'] == processor.Instruction.i_and:
                    self._set_flags_logic(instruction['destination']['name'], work_value, mask)

                elif instruction['instruction'] == processor.Instruction.i_or:
                    self._set_flags_logic(instruction['destination']['name'], work_value, mask)

                if instruction['destination']['type'] == processor.DestinationType.dt_reg:
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

                if instruction['shift_n'] > 0:
                    work_value >>= instruction['shift_n'] - 1

                    self.flag_carry = work_value & 1

                    work_value >>= 1

                self.set_register_value(register, work_value)

            elif instruction['instruction'] == processor.Instruction.i_rot_circ_r:  # z80: RRC
                register = instruction['destination']['name']

                work_value = self.get_register_value(register)

                bit_shift_n = self.registers[register]['width'] - 1

                for i in range(0, instruction['shift_n']):
                    old_0 = work_value & 1

                    self.flag_carry = old_0

                    work_value >>= 1

                    work_value |= old_0 << bit_shift_n

                self.set_register_value(register, work_value)

            elif instruction['instruction'] == processor.Instruction.i_rot_circ_l:
                register = instruction['destination']['name']

                work_value = self.get_register_value(register)

                mask = processor.masks[self.registers[register]['width']]

                for i in range(0, instruction['shift_n']):
                    old_carry = self.flag_carry

                    self.flag_carry = 1 if work_value & 128 else 0

                    work_value <<= 1

                    work_value &= mask

                    work_value |= old_carry

                self.set_register_value(register, work_value)

            else:
                assert False

    def gen_test_program(self):
        self.init_registers()

        program = []

        instruction: dict = {}
        instruction['instruction'] = processor.Instruction.i_load
        instruction['sources']     = [ { 'type': processor.SourceType.st_reg, 'name': 'B' } ]
        instruction['destination'] = {}
        instruction['destination']['type'] = processor.DestinationType.dt_reg
        instruction['destination']['name'] = 'A'
        instruction['opcode'] = f"LD {instruction['destination']['name']}, B"

        program.append(instruction)

        instruction: dict = {}
        instruction['instruction'] = processor.Instruction.i_add
        instruction['sources']     = [ { 'type': processor.SourceType.st_reg, 'name': 'A' }, { 'type': processor.SourceType.st_reg, 'name': 'C' } ]
        instruction['destination'] = {}
        instruction['destination']['type'] = processor.DestinationType.dt_reg
        instruction['destination']['name'] = 'A'
        instruction['opcode'] = f"ADD A, {instruction['sources'][0]['name']}"

        program.append(instruction)

        targets  = [
                    { 'initial_values': [ { 'width' : 8, 'value' : 0 },
                                          { 'width' : 8, 'value' : 0 } ],
                      'result_acc': 0 },
                    { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                          { 'width' : 8, 'value' : 1 } ],
                      'result_acc': 2 },
                    { 'initial_values': [ { 'width' : 8, 'value' : 32 },
                                          { 'width' : 8, 'value' : 16 } ],
                      'result_acc': 48 },
                   { 'initial_values': [ { 'width' : 8, 'value' : 16 },
                                          { 'width' : 8, 'value' : 32 } ],
                      'result_acc': 48 },
                   { 'initial_values': [ { 'width' : 8, 'value' : 254 },
                                          { 'width' : 8, 'value' : 8 } ],
                      'result_acc': 6 },
            ]

        return (program, targets)
