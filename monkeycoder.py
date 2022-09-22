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
max_n_miss             = max_program_length * 4  # 4 operation types (replace, append, delete, insert)

n_processes            = 11

best_lock = threading.Lock()
best_cost = 10000000
best_prog = None

def copy_program(program: List[dict]) -> List[dict]:
    return program[:]

# returns 0...x where 0 is perfect and x is bad
def test_program(proc, program, targets: List[dict], full: bool) -> float:
    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            n_targets_ok = 0
            break

        if proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    if full:
        return 11. - (float(n_targets_ok) / len(targets) * 10 + float(len(program)) / max_program_length), program

    return 1. - float(n_targets_ok) / len(targets)

def genetic_searcher(processor_obj, n_iterations):
    global best_cost
    global best_lock
    global best_prog
    global max_program_length
    global max_n_miss

    try:
        proc = processor_obj()

        with best_lock:
            local_best_cost = best_cost

        start = time.time()

        program = proc.generate_program(random.randint(0, max_program_length))

        work = None

        n_iterations = 0

        miss = 0

        while True:
            if len(program) == 0:
                program.append(proc.pick_an_instruction())

                work = copy_program(program)

            else:
                work = copy_program(program)

                idx = random.randint(0, len(work) - 1) if len(work) > 1 else 0

                while True:
                    action = random.choice([0, 1, 2, 3])

                    if len(work) < max_program_length or action == 0 or action == 2:
                        break

                if action == 0:  # replace
                    work[idx] = proc.pick_an_instruction()

                elif action == 1:  # insert
                    work.insert(idx, proc.pick_an_instruction())

                elif action == 2:  # delete
                    work.pop(idx)

                elif action == 3:  # append
                    work.append(proc.pick_an_instruction())

                else:
                    assert False

            if len(work) > 0:
                cost = test_program(proc, work, targets, False)

                if cost < local_best_cost:
                    local_best_cost = cost

                    program = work

                    miss = 0

                    with best_lock:
                        if best_cost > local_best_cost:
                            best_cost = local_best_cost
                            best_prog = program

                            print(time.time() - start, n_iterations, best_cost, len(program))

                else:
                    miss += 1

                    if miss >= max_n_miss:
                        miss = 0

                        random.seed()

                        program = proc.generate_program(random.randint(1, max_program_length))

            n_iterations += 1

    except Exception as e:
        print(f'Exception: {e}, line number: {e.__traceback__.tb_lineno}')

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

    thc = threading.Thread(target=genetic_searcher, args=(instantiate_processor_obj, n_iterations,))
    thc.start()

    thc.join()

    print('finish')

    for line in instantiate_processor_obj().get_program_init(targets[1]['initial_values']):
        print(line['opcode'])

    for line in best_prog:
        print(line['opcode'])
