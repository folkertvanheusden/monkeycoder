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
print(f'Number of processes: {n_processes}')

def copy_program(program: List[dict]) -> List[dict]:
    # return program[:]
    return program.copy()

# returns 0...x where 0 is perfect and x is bad
def test_program(proc: processor, program: List[dict], targets: List[dict], full: bool) -> float:
    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            n_targets_ok = 0
            sys.exit(1)
            break

        if proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    if full:
        mul = 1 / len(targets)

        return 11. - (float(n_targets_ok) * mul * 10 - float(len(program)) / max_program_length * mul), n_targets_ok == len(targets)

    return 1. - float(n_targets_ok) / len(targets), n_targets_ok == len(targets)

def genetic_searcher(processor_obj, targets, max_program_length: int, max_n_miss: int, cmd_q, result_q):
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
                    work.pop(idx)

                    for instruction in reversed(proc.pick_an_instruction(len(work) + 1)):
                        work.insert(idx, instruction)

                elif action == 1:  # insert
                    for instruction in reversed(proc.pick_an_instruction(len(work) + 1)):
                        work.insert(idx, instruction)

                elif action == 2:  # delete
                    work.pop(idx)

                elif action == 3:  # append
                    for instruction in proc.pick_an_instruction(len(work) + 1):
                        work.append(instruction)

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
    targets = []

    for i in range(0, 256, 7):
        j = (i * 13) & 255

        targets.append(
                { 'initial_values': [ { 'width' : 8, 'value' : i },
                                      { 'width' : 8, 'value' : j } ],
                  'result_acc': (i + j) & 255 }
                )

    return targets

def get_targets_shift_1():
    targets = []

    for i in range(0, 256, 7):
        targets.append(
                { 'initial_values': [ { 'width' : 8, 'value' : i },
                                      { 'width' : 8, 'value' : 1 } ],
                  'result_acc': (i << 1) & 255 }
                )

    return targets

def get_targets_shift_n():
    targets = []

    for i in range(0, 256, 7):
        targets.append(
                { 'initial_values': [ { 'width' : 8, 'value' : i },
                                      { 'width' : 8, 'value' : 3 } ],
                  'result_acc': (i << 3) & 255 }
                )

    return targets

def get_targets_shift_loop():
    targets = []

    for i in range(0, 256, 11):
        shift_n = (i * 13) & 7

        targets.append(
                { 'initial_values': [ { 'width' : 8, 'value' : i },
                                      { 'width' : 8, 'value' : shift_n } ],
                  'result_acc': (i << shift_n) & 255 }
                )

    return targets

def get_targets_multiply():
    targets = []

    for i in range(0, 256, 7):
        j = (i * 13) & 255

        targets.append(
                { 'initial_values': [ { 'width' : 8, 'value' : i },
                                      { 'width' : 8, 'value' : j } ],
                  'result_acc': (i * j) & 255 }
                )

    return targets

if __name__ == "__main__":
    # verify if monkeycoder works
    print('Verify...')
    proc = instantiate_processor_test()

    test_program_code, targets = proc.gen_test_program()

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], test_program_code) != False and proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    assert n_targets_ok == len(targets)

    print('Go!')
    targets = get_targets_shift_loop()

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

            if program is None:
                continue

            ok          = result[3]

            now         = time.time()

            one_ok |= ok

            if best_program is None or cost < best_cost:
                best_program    = program
                best_cost       = cost
                best_iterations = iterations

                tmp_file = '__.tmp.dat.-'

                fh = open(tmp_file, 'w')
                for line in best_program:
                    fh.write(f'{line["opcode"]}\n')
                fh.close()

                os.rename(tmp_file, 'current.asm')

                any_change = True

            elif cost == best_cost:
                if len(program) < len(best_program):
                    best_program    = program
                    best_iterations = iterations

                    any_change = True

        now    = time.time()
        t_diff = now - start_ts
        i_s    = iterations / t_diff

        if best_program != None:
            print(f'now: {now:.3f}, dt: {t_diff:6.3f}, cost: {best_cost:.6f}, length: {len(best_program)}, iterations: {best_iterations}, current iterations: {iterations}, i/s: {i_s:.2f}, ok: {one_ok}')

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
        proces.join()

    print('Bye')
