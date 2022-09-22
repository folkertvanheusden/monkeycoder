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

max_program_iterations = None
max_program_length     = 512
n_iterations           = 16384

n_processes            = 11

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

def linear_searcher(processor_obj, n_iterations):
    print('linear searcher')

    proc = processor_obj()

    best_cost = 1000000
    best_seed = None

    start = time.time()

    for i in range(0, n_iterations):
        cost = test_program(proc, targets, i)

        if cost < best_cost:
            best_cost = cost
            best_seed = i

            print(time.time() - start, n_iterations - i, best_seed, best_cost)

def random_searcher(processor_obj, n_iterations):
    print('random searcher')

    proc = processor_obj()

    r = random.Random()

    best_cost = 1000000
    best_seed = None

    start = time.time()

    for i in range(0, n_iterations):
        s = random.randint(0, 2**53 - 1)

        cost = test_program(proc, targets, s)

        if cost < best_cost:
            best_cost = cost
            best_seed = s

            print(time.time() - start, n_iterations - i, best_seed, best_cost)

def hill_climbing_searcher(processor_obj, n_iterations):
    print('hill climbing searcher')

    proc = processor_obj()

    r = random.Random()

    best_cost = 1000000
    best_seed = None

    n_to_do = n_iterations

    start = time.time()

    while n_to_do > 0:
        seed = random.randint(0, 2**53 - 1)

        cost = test_program(proc, targets, seed)

        n_to_do -= 1

        seed_low = seed - 1

        n_low = 0

        while n_to_do > 0:
            cost_low = test_program(proc, targets, seed_low)

            n_to_do -= 1

            if cost_low >= cost:
                break

            cost = cost_low

            seed_low -= 1

            n_low += 1

            if cost < best_cost:
                best_cost = cost
                best_seed = seed_low

                print(time.time() - start, n_to_do, best_seed, best_cost, f'#low: {n_low}')

        seed_high = seed + 1

        n_high = 0

        while n_to_do > 0:
            cost_high = test_program(proc, targets, seed_high)

            n_to_do -= 1

            if cost_high >= cost:
                break

            cost = cost_high

            seed_high = seed + 1

            n_high += 1

            if cost < best_cost:
                best_cost = cost
                best_seed = seed_high

                print(time.time() - start, n_to_do, best_seed, best_cost, f'#high: {n_high}')

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

    linear_searcher(instantiate_processor_obj, n_iterations)

    print()

    random_searcher(instantiate_processor_obj, n_iterations)

    print()

    hill_climbing_searcher(instantiate_processor_obj, n_iterations)

    print()
