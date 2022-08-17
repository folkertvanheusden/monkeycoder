#! /usr/bin/python3

import copy
from processor_z80 import processor_z80
import multiprocessing
import random
import time

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
    ]

max_program_iterations = None
max_program_length     = 256
max_modify_iterations  = 100

n_processes = 3

def test_program(p, targets, program):
    ok = True

    n_targets_ok = 0

    for target in targets:
        if p.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            ok = False
            break

        if p.get_accumulator() != target['result_acc']:
            ok = False

        else:
            n_targets_ok += 1

    return (ok, n_targets_ok)

def search(stop_q, out_q):
    random.seed()

    best_length = max_program_length + 1

    iterations   = 0
    n_targets_ok = 0

    p = processor_z80()

    while max_program_iterations == None or iterations < max_program_iterations:
        try:
            if stop_q.get_nowait() == 'stop':
                break

            break

        except Exception as e:
            pass

        # search for a program
        iterations += 1

        program = p.generate_program(max_program_length)

        rc = test_program(p, targets, program)
        ok = rc[0]

        n_targets_ok += rc[1]

        if ok:
            len_ = len(program)

            if len_ < best_length:
                best_length = len_

                out_q.put((program, n_targets_ok, iterations, True))

                iterations   = 0
                n_targets_ok = 0

        elif iterations >= 1000:
            out_q.put((None, n_targets_ok, iterations, False))

            iterations   = 0
            n_targets_ok = 0

        # see if it can be enhanced to make into something that
        # does work
        if not ok and rc[1] > 0:
            for mi in range(0, max_modify_iterations):
                work = copy.deepcopy(program)

                if len(work) < 2:
                    break

                replace_n = random.randint(1, len(work))

                for mri in range(0, replace_n):
                    idx = random.randint(0, len(work) - 1)

                    action = random.choice([0, 1, 2])

                    if action == 0:  # replace
                        work[idx] = p.pick_an_instruction()

                    elif action == 1:  # insert
                        work.insert(idx, p.pick_an_instruction())

                    elif action == 2:  # delete
                        del work[idx]

                    else:
                        assert False

                modify_rc = test_program(p, targets, work)
                if modify_rc[0] or modify_rc[1] > rc[1]:  # finished or improved?

                    if modify_rc[1] >= 3:
                        print()
                        print(mi, rc, '=>', modify_rc)

                    program = work

                    if modify_rc[0]:  # finished?
                        out_q.put((program, modify_rc[1], iterations, True))

                        break

    out_q.put(None)

stop_q = multiprocessing.Queue()
data_q = multiprocessing.Queue()

start_ts = time.time()
prev_ts  = start_ts

processes = []

for tnr in range(0, n_processes):
    proces = multiprocessing.Process(target=search, args=(stop_q, data_q,))
    proces.start()

    processes.append(proces)

iterations = 0

best_program    = None
best_iterations = None
first_output    = True

targets_ok_n     = 0

while True:
    result = data_q.get()
    
    if result == None:
        break

    iterations += result[2]

    if result[1] != None:
        targets_ok_n += result[1]

    if result[3] == True:
        program = result[0]

        if ok and (best_program == None or len(program) < len(best_program)):
            best_program    = program

            best_iterations = iterations

            if first_output:
                first_output = False

                print()
                print(f'First output after {iterations} iterations ({time.time() - start_ts:.2f} seconds)')

            if max_program_iterations == None:
                break

    now = time.time()

    if now - prev_ts >= 2:
        prev_ts = now

        diff_ts = now - start_ts

        print(f'Iterations done: {iterations}, average n_ok: {targets_ok_n / iterations:.4f}[{targets_ok_n}], run time: {now - start_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second\r', end='')

for proces in processes:
    stop_q.put('stop')

for proces in processes:
    proces.join()

n_deleted     = 0

p = processor_z80()

if best_program != None:
    idx = 0

    while idx < len(best_program):
        work = copy.deepcopy(best_program)

        del work[idx]

        rc = test_program(p, targets, work)
        ok = rc[0]

        if ok:
            best_program = work

            n_deleted += 1

        else:
            idx += 1

if best_program != None:
    best_program = p.get_program_init(targets[0]['initial_values']) + best_program

end_ts = time.time()

print()

if best_program != None:
    diff_ts = end_ts - start_ts

    print(f'Iterations: {best_iterations}, length program: {len(best_program)}, took: {diff_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second, # deleted: {n_deleted}')

    for instruction in best_program:
        print(instruction['opcode'])

else:
    print(f'Did not succeed in {iterations} iterations')
