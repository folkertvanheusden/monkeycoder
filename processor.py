import random

class processor:
    def __init__(self, init_registers_with):
        self.init_registers_with = init_registers_with

        self.init_registers()

        self.reset_registers()

        self.reset_ram()

        assert len(self.registers) > 0

        for reg in self.registers:
            r = self.registers[reg]

            assert r['width'] == 8 or r['width'] == 16 or r['width'] == 32 or r['width'] == 64   # TODO make this check smarter

            assert r['in_use'] == False

            if r['affects'] != None:  # register-pair
                for a in r['affects']:
                    assert a in self.registers

        assert len(self.operations) > 0

        for o in self.operations:
            op = self.operations[o]

            assert 'generate' in op
            assert op['generate'] != None

            assert 'targets'  in op
            for t in op['targets']:
                assert t['name'] in self.registers

                assert t['width'] == 8 or t['width'] == 16 or t['width'] == 32 or t['width'] == 64   # TODO make this check smarter

            assert 'sources'  in op
            for s in op['targets']:
                assert s['name'] in self.registers

                assert s['width'] == 8 or s['width'] == 16 or s['width'] == 32 or s['width'] == 64   # TODO make this check smarter

        assert len(self.indirect) > 0

        for i in self.indirect:
            ind = self.indirect[i]

            assert ind['width'] == 8 or ind['width'] == 16 or ind['width'] == 32 or ind['width'] == 64   # TODO make this check smarter

            for rf in ind['affects']:
                assert rf in self.registers

    def reset_registers(self):
        used_list = []
        for action in self.init_registers_with:
            reg = self.allocate_random_register(action['width'])

            reg[1]['value'] = action['value']

            used_list.append(reg[0])

        for reg in used_list:
            self.free_register(reg)

    def reset_ram(self):
        self.ram = [ 0 ] * self.ram_size

    def allocate_random_register(self, width):
        for r in self.registers:
            reg = self.registers[r]

            if reg['width'] == width and reg['in_use'] == False:
                reg['in_use'] = True

                return (r, reg)

        assert False

    def allocate_register(self, name):
        assert self.registers[name]['in_use'] == False

        self.registers[name]['in_use'] = True

        return (name, self.registers[name])

    def free_register(self, name):
        r = self.registers[name]

        assert r['in_use'] == True

        r['in_use'] = False

    def any_register_in_use(self, reg_list):
        for r in reg_list:
            if self.registers[r]['in_use'] == True:
                return True

        return False

    def allocate_random_indirect(self, width):
        for reg in self.indirect:
            r = self.indirect[reg]

            if r['width'] == width and self.any_register_in_use(r['affects']) == False:
                for ra in r['affects']:
                    self.registers[ra]['in_use'] = True

                return (reg, r)

        assert False

    def get_register_pair_16(self, reg_msb, reg_lsb):
        return (self.registers[reg_msb]['value'] << 8) | self.registers[reg_lsb]['value']

    def pick_operation(self):
        instruction = random.choice(list(self.operations))

        operation = self.operations[instruction]['generate']()

        return operation
