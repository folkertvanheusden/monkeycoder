#! /usr/bin/python3

from processor import processor
from processor_z80 import processor_z80
from processor_test import processor_test
import random
import threading
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

best_lock = threading.Lock()
best_cost = 10000000
best_seed = None
best_prog = None

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

    return 11. - (float(n_targets_ok) / len(targets) * 10 + float(len(program)) / max_program_length), program

def linear_searcher(processor_obj, n_iterations):
    global best_cost
    global best_lock
    global best_prog
    global best_seed

    try:
        proc = processor_obj()

        local_best_cost = 1000000
        local_best_seed = None

        start = time.time()

        for i in range(0, n_iterations):
            cost, program = test_program(proc, targets, i)

            if cost < local_best_cost:
                local_best_cost = cost
                local_best_seed = i

                with best_lock:
                    if best_cost > local_best_cost:
                        best_cost = local_best_cost
                        best_seed = local_best_seed
                        best_prog = program

                        print('L  ', time.time() - start, n_iterations - i, best_seed, best_cost)

    except Exception as e:
        print('linear', e)

def random_searcher(processor_obj, n_iterations):
    global best_cost
    global best_lock
    global best_prog
    global best_seed

    try:
        proc = processor_obj()

        r = random.Random()

        local_best_cost = 1000000
        local_best_seed = None

        start = time.time()

        for i in range(0, n_iterations):
            s = random.randint(0, 2**53 - 1)

            cost, program = test_program(proc, targets, s)

            if cost < local_best_cost:
                local_best_cost = cost
                local_best_seed = s

                with best_lock:
                    if best_cost > local_best_cost:
                        best_cost = local_best_cost
                        best_seed = local_best_seed
                        best_prog = program

                        print('R  ', time.time() - start, n_iterations - i, best_seed, best_cost)

    except Exception as e:
        print('random', e)

def hill_climbing_searcher(processor_obj, n_iterations):
    global best_cost
    global best_lock
    global best_prog
    global best_seed

    try:
        proc = processor_obj()

        r = random.Random()

        local_best_cost = 1000000
        local_best_seed = None

        n_to_do = n_iterations

        start = time.time()

        while n_to_do > 0:
            seed = random.randint(0, 2**53 - 1)

            cost, program = test_program(proc, targets, seed)

            if cost < local_best_cost:
                local_best_cost = cost
                local_best_seed = seed

                with best_lock:
                    if best_cost > local_best_cost:
                        best_cost = local_best_cost
                        best_seed = local_best_seed
                        best_prog = program

                        print('H-S', time.time() - start, n_to_do, best_seed, best_cost)

            n_to_do -= 1

            seed_low = seed - 1

            while n_to_do > 0:
                cost_low, program = test_program(proc, targets, seed_low)

                n_to_do -= 1

                if cost_low >= cost:
                    break

                cost = cost_low

                seed_low -= 1

                if cost < local_best_cost:
                    local_best_cost = cost
                    local_best_seed = seed_low

                    with best_lock:
                        if best_cost > local_best_cost:
                            best_cost = local_best_cost
                            best_seed = local_best_seed
                            best_prog = program

                            print('H-L', time.time() - start, n_to_do, best_seed, best_cost)

            seed_high = seed + 1

            while n_to_do > 0:
                cost_high, program = test_program(proc, targets, seed_high)

                n_to_do -= 1

                if cost_high >= cost:
                    break

                cost = cost_high

                seed_high = seed + 1

                if cost < local_best_cost:
                    local_best_cost = cost
                    local_best_seed = seed_high

                    with best_lock:
                        if best_cost > local_best_cost:
                            best_cost = local_best_cost
                            best_seed = local_best_seed
                            best_prog = program

                            print('H-R', time.time() - start, n_to_do, best_seed, best_cost)

    except Exception as e:
        print('hill climbing', e)

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
               { 'initial_values': [ { 'width' : 8, 'value' : 19 },
                                      { 'width' : 8, 'value' : 31 } ],
                  'result_acc': 77 },
               { 'initial_values': [ { 'width' : 8, 'value' : 140 },
                                      { 'width' : 8, 'value' : 202 } ],
                  'result_acc': 120 },
               { 'initial_values': [ { 'width' : 8, 'value' : 201 },
                                      { 'width' : 8, 'value' : 153 } ],
                  'result_acc': 33 },
        ]

    tl = threading.Thread(target=linear_searcher, args=(instantiate_processor_obj, n_iterations,))
    tl.start()

    tr = threading.Thread(target=random_searcher, args=(instantiate_processor_obj, n_iterations,))
    tr.start()

    thc = threading.Thread(target=hill_climbing_searcher, args=(instantiate_processor_obj, n_iterations,))
    thc.start()

    thc.join()

    tr.join()

    tl.join()

    for line in best_prog:
        print(line['opcode'])
