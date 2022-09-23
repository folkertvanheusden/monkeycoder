#! /usr/bin/python3

from processor import processor
from processor_z80 import processor_z80
from processor_test import processor_test
import multiprocessing
import os
import random
import sys
import time
from typing import List

def instantiate_processor_z80():
    return processor_z80()

def instantiate_processor_test():
    return processor_test()

instantiate_processor_obj = instantiate_processor_z80

max_program_iterations = None
max_program_length     = 512
max_n_miss             = max_program_length * 4  # 4 operation types (replace, append, delete, insert)

n_processes            = multiprocessing.cpu_count()

def copy_program(program: List[dict]) -> List[dict]:
    return program[:]

# returns 0...x where 0 is perfect and x is bad
def test_program(proc: processor, program: List[dict], targets: List[dict], full: bool) -> float:
    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            n_targets_ok = 0
            break

        if proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    if full:
        return 11. - (float(n_targets_ok) / len(targets) * 10 - float(len(program)) / max_program_length), n_targets_ok == len(targets)

    return 1. - float(n_targets_ok) / len(targets), n_targets_ok == len(targets)

def genetic_searcher(processor_obj, targets, max_program_length, max_n_miss, cmd_q, result_q):
    try:
        proc = processor_obj()

        local_best_cost = 1000000

        local_best_prog = None

        local_best_ok   = False

        start = time.time()

        program = proc.generate_program(random.randint(1, max_program_length))

        work = None

        n_iterations = 0

        miss = 0

        while True:
            try:
                cmd = cmd_q.get_nowait()

                if cmd == 'results':
                    result_q.put((n_iterations, local_best_cost, local_best_prog, local_best_ok))

                    n_iterations = 0

                elif cmd == 'stop':
                    break

            except Exception as e:
                pass

            work = copy_program(program)

            n_actions = random.randint(1, 8)

            for i in range(0, n_actions):
                len_work = len(work)

                idx = random.randint(0, len_work - 1) if len_work > 1 else 0

                if len_work == 0:
                    action = 3

                elif len_work >= max_program_length:
                    action = random.choice([0, 2, 4])

                else:
                    action = random.choice([0, 1, 2, 3, 4])

                if action == 0:  # replace
                    work[idx] = proc.pick_an_instruction()

                elif action == 1:  # insert
                    work.insert(idx, proc.pick_an_instruction())

                elif action == 2:  # delete
                    work.pop(idx)

                elif action == 3:  # append
                    work.append(proc.pick_an_instruction())

                elif action == 4:  # swap
                    idx2 = random.randint(0, len_work - 1) if len_work > 1 else 0

                    if idx != idx2:
                        work[idx], work[idx2] = work[idx2], work[idx]

                else:
                    assert False

            if len(work) > 0:
                cost, ok = test_program(proc, work, targets, True)
                
                if cost <= local_best_cost:
                    local_best_cost = cost
                    local_best_prog = copy_program(work)
                    local_best_ok   = ok

                    program = work

                    miss = 0

                else:
                    miss += 1

                    if miss >= max_n_miss:
                        miss = 0

                        random.seed()

                        program = proc.generate_program(random.randint(1, max_program_length))

            n_iterations += 1

    except Exception as e:
        print(f'Exception: {e}, line number: {e.__traceback__.tb_lineno}')

    print('Process is terminating...')

    sys.exit(0)

def get_targets_add():
    return [
                { 'initial_values': [ { 'width' : 8, 'value' : 0 },
                                      { 'width' : 8, 'value' : 0 } ],
                  'result_acc': 0 },
                { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                      { 'width' : 8, 'value' : 1 } ],
                  'result_acc': 4 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                      { 'width' : 8, 'value' : 3 } ],
                  'result_acc': 4 },
                { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                       { 'width' : 8, 'value' : 3 } ],
                   'result_acc': 6 },
                { 'initial_values': [ { 'width' : 8, 'value' : 8 },
                                       { 'width' : 8, 'value' : 8 } ],
                   'result_acc': 16 },
                { 'initial_values': [ { 'width' : 8, 'value' : 19 },
                                       { 'width' : 8, 'value' : 31 } ],
                   'result_acc': 50 },
                { 'initial_values': [ { 'width' : 8, 'value' : 140 },
                                       { 'width' : 8, 'value' : 202 } ],
                   'result_acc': 86 },
                { 'initial_values': [ { 'width' : 8, 'value' : 201 },
                                       { 'width' : 8, 'value' : 153 } ],
                   'result_acc': 98 },
        ]

def get_targets_shift_1():
    return [
                { 'initial_values': [ { 'width' : 8, 'value' : 0 },
                                      { 'width' : 8, 'value' : 1 } ],
                  'result_acc': 0 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                      { 'width' : 8, 'value' : 1 } ],
                  'result_acc': 2 },
                { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                       { 'width' : 8, 'value' : 1 } ],
                   'result_acc': 6 },
                { 'initial_values': [ { 'width' : 8, 'value' : 193 },
                                       { 'width' : 8, 'value' : 1 } ],
                   'result_acc': 130 },
        ]

def get_targets_shift_n():
    return [
                { 'initial_values': [ { 'width' : 8, 'value' : 0 },
                                      { 'width' : 8, 'value' : 3 } ],
                  'result_acc': 0 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                      { 'width' : 8, 'value' : 3 } ],
                  'result_acc': 8 },
                { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                       { 'width' : 8, 'value' : 3 } ],
                   'result_acc': 24 },
                { 'initial_values': [ { 'width' : 8, 'value' : 193 },
                                       { 'width' : 8, 'value' : 3 } ],
                   'result_acc': 8 },
        ]

def get_targets_shift_loop():
    return [
                { 'initial_values': [ { 'width' : 8, 'value' : 0 },
                                      { 'width' : 8, 'value' : 0 } ],
                  'result_acc': 0 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                      { 'width' : 8, 'value' : 0 } ],
                  'result_acc': 1 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                      { 'width' : 8, 'value' : 1 } ],
                  'result_acc': 2 },
                { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                       { 'width' : 8, 'value' : 2 } ],
                   'result_acc': 4 },
                { 'initial_values': [ { 'width' : 8, 'value' : 3 },
                                       { 'width' : 8, 'value' : 3 } ],
                   'result_acc': 24 },
                { 'initial_values': [ { 'width' : 8, 'value' : 9 },
                                       { 'width' : 8, 'value' : 5 } ],
                   'result_acc': 32 },
                { 'initial_values': [ { 'width' : 8, 'value' : 193 },
                                       { 'width' : 8, 'value' : 7 } ],
                   'result_acc': 128 },
        ]

def get_targets_multiply():
    return [
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

if __name__ == "__main__":
    # verify if monkeycoder works
    proc = instantiate_processor_test()

    test_program_code, targets = proc.gen_test_program()

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], test_program_code) != False and proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    assert n_targets_ok == len(targets)

    targets = get_targets_shift_n()

    result_q: multiprocessing.Queue = multiprocessing.Manager().Queue()

    prev_now = 0

    start_ts = time.time()

    processes = []
    cmd_qs    = []

    for tnr in range(0, n_processes):
        cmd_q: multiprocessing.Queue = multiprocessing.Manager().Queue()
        cmd_qs.append(cmd_q)

        proces = multiprocessing.Process(target=genetic_searcher, args=(instantiate_processor_obj, targets, max_program_length, max_n_miss, cmd_q, result_q,))
        proces.start()

        processes.append(proces)

    iterations = 0

    best_program    = None
    best_cost       = 1000000
    best_iterations = None

    first_output    = True

    while True:
        one_ok     = False

        any_change = False

        for q in cmd_qs:
            q.put('results')

            result      = result_q.get()

            iterations += result[0]

            cost        = result[1]

            program     = result[2]

            ok          = result[3]

            now         = time.time()

            one_ok |= ok

            if (best_program is None) or cost < best_cost:
                best_program    = program
                best_cost       = cost
                best_iterations = iterations

                fh = open('__.tmp.dat', 'w')
                for line in best_program:
                    fh.write(f'{line["opcode"]}\n')
                fh.close()

                os.rename('__.tmp.dat', 'current.asm')

                any_change = True

            elif cost == best_cost:
                if len(program) < len(best_program):
                    best_program    = program
                    best_iterations = iterations

                    any_change = True

        now    = time.time()
        t_diff = now - start_ts
        i_s    = iterations / t_diff

        print(f'now: {now:.3f}, dt: {t_diff:.3f}, cost: {best_cost:.3f}, length: {len(best_program)}, iterations: {best_iterations}, current iterations: {iterations}, i/s: {i_s:.2f}, ok: {one_ok}')

        if any_change == False and one_ok == True:
            break

        time.sleep(5)

    end_ts = time.time()

    proc = instantiate_processor_obj()

    best_program = proc.get_program_init(targets[0]['initial_values']) + best_program

    print()

    if best_program is not None:
        diff_ts = end_ts - start_ts

        print(f'Iterations: {best_iterations}, length program: {len(best_program)}, took: {diff_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second')

        for instruction in best_program:
            print(instruction['opcode'])

    else:
        print(f'Did not succeed in {iterations} iterations')

    print('Finishing processes...')

    for q in cmd_qs:
        q.put('stop')

    print('Wait for the processes to stop...')

    for proces in multiprocessing.active_children():
        proces.join(0.001)

    print('Bye')
