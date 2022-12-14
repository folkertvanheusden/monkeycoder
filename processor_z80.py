import logging
from processor import processor
import random
from typing import Dict, List

class processor_z80(processor):
    def __init__(self):
        super().__init__()

        self.ram_size = 65536

        self.init_registers()

        self.instr_mapping: dict = {}
        self.instr_mapping[processor.Instruction.i_add       ] = 'ADD'
        self.instr_mapping[processor.Instruction.i_add_carry ] = 'ADC'
        self.instr_mapping[processor.Instruction.i_sub       ] = 'SUB'
        self.instr_mapping[processor.Instruction.i_sub_carry ] = 'SBC'
        self.instr_mapping[processor.Instruction.i_xor       ] = 'XOR'
        self.instr_mapping[processor.Instruction.i_and       ] = 'AND'
        self.instr_mapping[processor.Instruction.i_or        ] = 'OR'
        self.instr_mapping[processor.Instruction.i_load      ] = 'LD'
        self.instr_mapping[processor.Instruction.i_shift_r   ] = 'SRL'
        self.instr_mapping[processor.Instruction.i_rot_circ_r] = 'RRC'
        self.instr_mapping[processor.Instruction.i_rot_circ_l] = 'RLC'
        self.instr_mapping[processor.Instruction.i_inc       ] = 'INC'
        self.instr_mapping[processor.Instruction.i_dec       ] = 'DEC'

    def init_registers(self) -> None:
        self.registers: Dict[str, processor.registers_dict] = {
                'A': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'B': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'C': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'D': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'E': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'H': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'L': { 'width': 8, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': None, 'dest_allowed': True },
                'HL': { 'width': 16, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': ['H', 'L'], 'dest_allowed': True  },
                'BC': { 'width': 16, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': ['B', 'C'], 'dest_allowed': False },
                'DE': { 'width': 16, 'value': 0, 'ivalue' : None, 'set_': False, 'pair': ['D', 'E'], 'dest_allowed': False }
            }

    def get_program_init(self, initial_values: dict) -> List[dict]:
        self.reset_registers(initial_values)

        instructions: List[dict] = []

        for register in self.registers:
            is_pair = self.registers[register]['pair'] != None
            if is_pair:
                continue

            v = self.registers[register]['ivalue']
            if v == None:
                v = 0

            instruction: dict = {}
            instruction['instruction'] = processor.Instruction.i_load
            instruction['sources']     = [ { 'type': processor.SourceType.st_val, 'value': v } ]
            instruction['destination'] = {}
            instruction['destination']['type'] = processor.DestinationType.dt_reg
            instruction['destination']['name'] = register
            instruction['opcode'] = f"LD {instruction['destination']['name']}, {v}"

            instructions.append(instruction)

        return instructions

    def pick_an_instruction(self, program: dict, max_length: int) -> List[dict]:
        try:
            instructions: List[dict] = [ ]

            while len(instructions) == 0:
                instr_type: int = random.randint(0, 5)

                instruction: dict = { }

                if instr_type == 0:
                    sub_type = random.choice([ processor.Instruction.i_add, processor.Instruction.i_sub, processor.Instruction.i_xor, processor.Instruction.i_and, processor.Instruction.i_or, processor.Instruction.i_add_carry, processor.Instruction.i_sub_carry ])

                    instruction['instruction'] = sub_type

                    width = random.choice([8, 16]) if sub_type in [processor.Instruction.i_add, processor.Instruction.i_add_carry, processor.Instruction.i_sub_carry] else 8

                    source1 = { 'type': processor.SourceType.st_reg, 'name': self.get_accumulator_name() }  # add a,b => a = a + b
                    source2 = { 'type': processor.SourceType.st_reg, 'name': self.pick_a_register(width, None) } if random.choice([True, False]) or width == 16 else { 'type': processor.SourceType.st_val, 'value': random.randint(0, 255) }
                    instruction['sources']     = [ source1, source2 ]

                    instruction['destination'] = {}
                    instruction['destination']['type'] = processor.DestinationType.dt_reg
                    instruction['destination']['name'] = 'A' if width == 8 else 'HL'

                    if source2['type'] == processor.SourceType.st_reg:
                        instruction['opcode'] = f"{self.instr_mapping[sub_type]} {instruction['destination']['name']}, {source2['name']}"
                    
                    elif source2['type'] == processor.SourceType.st_val:
                        instruction['opcode'] = f"{self.instr_mapping[sub_type]} {instruction['destination']['name']}, ${source2['value']:x}"

                    else:
                        assert False

                    instructions.append(instruction)

                elif instr_type == 1:
                    instruction['instruction'] = processor.Instruction.i_load

                    instruction['destination'] = {}
                    instruction['destination']['type'] = processor.DestinationType.dt_reg
                    instruction['destination']['name'] = self.pick_a_register(8, True)

                    if random.randint(0, 1) == 0:
                        instruction['destination']['name'] = self.pick_a_register(8, True)

                        register = self.pick_a_register(8, True)

                        instruction['sources'] = [ { 'type': processor.SourceType.st_reg, 'name': register } ]
                        instruction['opcode'] = f"LD {instruction['destination']['name']}, {register}"

                    else:
                        width = random.choice([8, 16])

                        instruction['destination']['name'] = self.pick_a_register(width, True)

                        v = random.randint(0, 255) if width == 8 else random.randint(0, 65535)

                        instruction['sources'] = [ { 'type': processor.SourceType.st_val, 'value': v } ]
                        instruction['opcode'] = f"LD {instruction['destination']['name']}, ${v:x}"

                    instructions.append(instruction)

                elif instr_type == 2:
                    sub_instr_type = random.choice([0, 1, 2])

                    if sub_instr_type == 0:
                        instruction['instruction'] = processor.Instruction.i_shift_r
                        instruction['shift_n']     = 1  # Z80 can only shift 1 bit at a time

                        instruction['destination'] = {}
                        instruction['destination']['type'] = processor.DestinationType.dt_reg
                        instruction['destination']['name'] = self.pick_a_register(8, True)

                        instruction['opcode'] = f"SRL {instruction['destination']['name']}"

                    elif sub_instr_type == 1:
                        instruction['instruction'] = processor.Instruction.i_rot_circ_r
                        instruction['shift_n']     = 1  # Z80 can only shift 1 bit at a time

                        instruction['destination'] = {}
                        instruction['destination']['type'] = processor.DestinationType.dt_reg
                        instruction['destination']['name'] = self.pick_a_register(8, True)

                        instruction['opcode'] = f"RRC {instruction['destination']['name']}"

                    elif sub_instr_type == 2:
                        instruction['instruction'] = processor.Instruction.i_rot_circ_l
                        instruction['shift_n']     = 1  # Z80 can only shift 1 bit at a time

                        instruction['destination'] = {}
                        instruction['destination']['type'] = processor.DestinationType.dt_reg
                        instruction['destination']['name'] = self.pick_a_register(8, True)

                        instruction['opcode'] = f"RLC {instruction['destination']['name']}"

                    else:
                        assert False

                    instructions.append(instruction)

                elif instr_type == 3:
                    sub_instr_type = random.choice([0, 1, 2])

                    if sub_instr_type == 0:  # set carry flag
                        instruction['instruction'] = processor.Instruction.i_set_carry
                        instruction['opcode'] = 'SCF'

                        instructions.append(instruction)

                    elif sub_instr_type == 1:  # clear carry flag
                        instruction1 = { }
                        instruction1['instruction'] = processor.Instruction.i_set_carry
                        instruction1['opcode'] = 'SCF'

                        instructions.append(instruction1)

                        instruction2 = { }
                        instruction2['instruction'] = processor.Instruction.i_complement_carry
                        instruction2['opcode'] = 'CCF'

                        instructions.append(instruction2)

                    elif sub_instr_type == 2:  # complement carry flag
                        instruction['instruction'] = processor.Instruction.i_complement_carry
                        instruction['opcode'] = 'CCF'

                        instructions.append(instruction)

                    else:
                        assert False

                elif instr_type == 4:
                    cur_prog_len = len(program['code'])

                    if cur_prog_len > 0:
                        sub_instr_type = random.choice([0, 1, 2, 3])

                        addr = random.randint(0, cur_prog_len - 1) if cur_prog_len > 1 else 0

                        if 'label' in program['code'][addr]:
                            label = program['code'][addr]['label']

                        else:
                            label = f"l_{program['label_count']:04x}"

                            program['label_count'] += 1

                            program['code'][addr]['label'] = label

                        if sub_instr_type == 0:
                            instr  = processor.Instruction.i_jump_c
                            opcode = f'JP C, {label}'

                        elif sub_instr_type == 1:
                            instr  = processor.Instruction.i_jump_nc
                            opcode = f'JP NC, {label}'

                        elif sub_instr_type == 2:
                            instr  = processor.Instruction.i_jump_z
                            opcode = f'JP Z, {label}'

                        elif sub_instr_type == 3:
                            instr  = processor.Instruction.i_jump_nz
                            opcode = f'JP NZ, {label}'
                        
                        else:
                            assert False

                        instruction['instruction']       = instr
                        instruction['destination_label'] = label
                        instruction['opcode']            = opcode

                        instructions.append(instruction)

                elif instr_type == 5:
                    sub_instr_type = random.choice([0, 1])

                    instruction['instruction'] = processor.Instruction.i_dec if sub_instr_type == 0 else processor.Instruction.i_inc

                    width = random.choice([8, 16])

                    instruction['destination'] = {}
                    instruction['destination']['type'] = processor.DestinationType.dt_reg
                    instruction['destination']['name'] = self.pick_a_register(width, None)

                    instruction['opcode'] = f"{'DEC' if sub_instr_type == 0 else 'INC'} {instruction['destination']['name']}"

                    instructions.append(instruction)

                else:
                    assert False

            return instructions

        except Exception as e:
            logging.error(f'Exception: {e}, line number: {e.__traceback__.tb_lineno} (processor_z80)')

        assert False

    def _set_flags_add(self, instruction: processor.Instruction, dest, dest_value, mask):
        final_dest_value   = dest_value & mask

        if instruction != processor.Instruction.i_add:
            self.flag_zero = final_dest_value == 0

        self.flag_negative = False
        self.flag_carry    = (dest_value & (mask + 1)) != 0

    def _set_flags_inc_dec(self, instruction: processor.Instruction, dest, dest_value, mask):
        final_dest_value   = dest_value & mask

        self.flag_negative = False if instruction == processor.Instruction.i_inc else True
        self.flag_zero     = final_dest_value == 0

    def _set_flags_sub(self, instruction: processor.Instruction, dest, dest_value, mask):
        final_dest_value   = dest_value & mask

        self.flag_carry    = (dest_value & (mask + 1)) != 0
        self.flag_zero     = final_dest_value == 0
        self.flag_negative = True

    def _set_flags_logic(self, instruction: processor.Instruction, dest, dest_value, mask):
        final_dest_value   = dest_value & mask

        self.flag_carry    = False
        self.flag_zero     = final_dest_value == 0
        self.flag_negative = False

    def get_accumulator_name(self) -> str:
        return 'A'
