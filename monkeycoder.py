#! /usr/bin/python3

from processor import processor
from processor_z80 import processor_z80
from processor_test import processor_test
import multiprocessing
import random
import time
from typing import List

def instantiate_processor_z80():
    return processor_z80()

def instantiate_processor_test():
    return processor_test()

instantiate_processor_obj = instantiate_processor_z80

max_program_iterations    = None
max_program_length        = 512
max_modify_iterations     = 16
max_modifications_per_run = 16

n_processes = 31

def copy_program(program: List[dict]) -> List[dict]:
    return program[:]

# returns 0...x where 0 is perfect and x is bad
def test_program(proc, targets: List[dict], seed: int) -> float:
    program = proc.generate_program(seed, max_program_length)

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            n_targets_ok = 0
            break

        if proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    return 11. - (float(n_targets_ok) / len(targets) * 10 + float(len(program)) / max_program_length)

if __name__ == "__main__":
    # verify if monkeycoder works
    proc = instantiate_processor_test()

    test_program_code, targets = proc.gen_test_program()

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], test_program_code) != False and proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    assert n_targets_ok == len(targets)

    targets  = [
                { 'initial_values': [ { 'width' : 8, 'value' : 0 },
                                      { 'width' : 8, 'value' : 0 } ],
                  'result_acc': 0 },
                { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                      { 'width' : 8, 'value' : 1 } ],
                  'result_acc': 3 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                      { 'width' : 8, 'value' : 3 } ],
                  'result_acc': 3 },
               { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                      { 'width' : 8, 'value' : 3 } ],
                  'result_acc': 9 },
               { 'initial_values': [ { 'width' : 8, 'value' : 8 },
                                      { 'width' : 8, 'value' : 8 } ],
                  'result_acc': 64 },
        ]

    proc = instantiate_processor_obj()

    # r = random.Random()

    best_cost = 1000000
    best_seed = None

    start = time.time()

    i = 0

    # do search
    while True:
        cost = test_program(proc, targets, i)

        if cost < best_cost:
            best_cost = cost
            best_seed = i

            print(time.time() - start, best_seed, best_cost)

        i += 1
