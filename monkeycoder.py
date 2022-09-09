#! /usr/bin/python3

import copy
from processor import processor
from processor_z80 import processor_z80
import multiprocessing
from random import SystemRandom
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
           { 'initial_values': [ { 'width' : 8, 'value' : 254 },
                                  { 'width' : 8, 'value' : 8 } ],
              'result_acc': 7 },
    ]

rng = SystemRandom()

def instantiate_processor_z80():
    return processor_z80()

instantiate_processor_obj = instantiate_processor_z80

max_program_iterations    = None
max_program_length        = 128
max_modify_iterations     = 16
max_modifications_per_run = 16

n_processes = 31

def test_program(proc, targets: list[dict], program: list[dict]):
    ok = True

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            ok = False
            break

        if proc.get_accumulator() != target['result_acc']:
            ok = False

        else:
            n_targets_ok += 1

    return (ok, n_targets_ok)

def search(stop_q: multiprocessing.Queue, out_q: multiprocessing.Queue, instantiate_processor) -> None:
    best_length = max_program_length + 1

    iterations   = 0
    n_targets_ok = 0

    proc = instantiate_processor()

    while max_program_iterations is None or iterations < max_program_iterations:
        try:
            if stop_q.get_nowait() == 'stop':
                break

            break

        except Exception as e:
            pass

        # search for a program
        iterations += 1

        program = proc.generate_program(max_program_length)

        rc = test_program(proc, targets, program)
        ok = rc[0]

        n_targets_ok += rc[1]

        if ok:
            len_ = len(program)

            if len_ < best_length:
                best_length = len_

                out_q.put((program, n_targets_ok, iterations, True))

                iterations   = 0
                n_targets_ok = 0

        elif iterations >= 100:
            out_q.put((None, n_targets_ok, iterations, False))

            iterations   = 0
            n_targets_ok = 0

        # see if it can be enhanced to make into something that
        # does work
        if not ok and rc[1] > 0:
            for mi in range(0, max_modify_iterations):
                work = copy.deepcopy(program)

                operations_n = rng.randint(1, max_modifications_per_run)

                for mri in range(0, operations_n):
                    if len(work) < 2:
                        break

                    idx = rng.randint(0, len(work) - 1)

                    action = rng.choice([0, 1, 2, 3])

                    if action == 0:  # replace
                        work[idx] = proc.pick_an_instruction()

                    elif action == 1:  # insert
                        work.insert(idx, proc.pick_an_instruction())

                    elif action == 2:  # delete
                        del work[idx]

                    elif action == 3:  # append
                        work.append(proc.pick_an_instruction())

                    else:
                        assert False

                modify_rc = test_program(proc, targets, work)
                if modify_rc[0] or modify_rc[1] > rc[1]:  # finished or improved?
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
    proces = multiprocessing.Process(target=search, args=(stop_q, data_q, instantiate_processor_obj))
    proces.start()

    processes.append(proces)

iterations = 0

best_program    = None
best_iterations = None
first_output    = True

targets_ok_n     = 0

while True:
    result = data_q.get()

    if result is None:
        break

    iterations += result[2]

    if result[1] is not None:
        targets_ok_n += result[1]

    if result[3] == True:
        program = result[0]

        if best_program is None or len(program) < len(best_program):
            best_program    = program

            best_iterations = iterations

            if first_output:
                first_output = False

                print()
                print(f'First output after {iterations} iterations ({time.time() - start_ts:.2f} seconds)')

            if max_program_iterations is None:
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

p = instantiate_processor_obj()

if best_program is not None:
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

if best_program is not None:
    best_program = p.get_program_init(targets[0]['initial_values']) + best_program

end_ts = time.time()

print()

if best_program is not None:
    diff_ts = end_ts - start_ts

    print(f'Iterations: {best_iterations}, length program: {len(best_program)}, took: {diff_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second, # deleted: {n_deleted}')

    for instruction in best_program:
        print(instruction['opcode'])

else:
    print(f'Did not succeed in {iterations} iterations')
