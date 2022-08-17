#! /usr/bin/python3

import copy
from processor_z80 import processor_z80
import random
import threading
import time

targets  = [
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

random.seed()

max_program_iterations = None
max_program_length     = 256

iterations = 0

start_ts = time.time()
prev_ts  = start_ts

best_program    = None
best_iterations = None
first_output    = True

targets_ok_stat  = 0
targets_ok_n     = 0
targets_ok_bestn = 0
targets_ok_best  = None

stop = False

lock = threading.Lock()

def search():
    global iterations

    global stop

    global best_program
    global best_iterations
    global first_output

    global targets_ok_stat
    global targets_ok_n
    global targets_ok_bestn
    global targets_ok_best

    global prev_ts

    while True:
        lock.acquire()

        if not (stop == False and (max_program_iterations == None or iterations < max_program_iterations)):
            lock.release()
            break

        iterations += 1

        lock.release()

        p = processor_z80()
        program = p.generate_program(max_program_length)

        if program == None:
            continue

        rc = test_program(p, targets, program)
        ok = rc[0]

        lock.acquire()

        targets_ok_stat += rc[1]
        targets_ok_n    += 1

        if rc[1] > targets_ok_bestn:
            targets_ok_bestn = rc[1]
            targets_ok_best  = program

        if ok and (best_program == None or len(program) < len(best_program)):
            best_program    = program

            best_iterations = iterations

            if first_output:
                first_output = False

                print()
                print(f'First output after {iterations} iterations ({time.time() - start_ts:.2f} seconds)')

            if max_program_iterations == None:
                lock.release()
                break

        now = time.time()

        if now - prev_ts >= 2:
            prev_ts = now

            diff_ts = now - start_ts

            print(f'Iterations done: {iterations}, average n_ok: {targets_ok_stat / targets_ok_n:.4f}[{targets_ok_bestn}], run time: {now - start_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second\r', end='')

        lock.release()

    stop = True

threads = []

for tnr in range(0, 32):
    thread = threading.Thread(target=search)
    thread.start()

    threads.append(thread)

for thread in threads:
    thread.join()

n_deleted     = 0

if best_program != None:
    idx = 0

    p = processor_z80()

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
