#! /usr/bin/python3

from processor_z80 import processor_z80
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

max_program_iterations = None
max_program_length     = 256

iterations = 0

start_ts   = time.time()
prev_ts    = start_ts

best_program    = None
best_iterations = None
first_output    = True

targets_ok_stat  = 0
targets_ok_n     = 0
targets_ok_bestn = 0
targets_ok_best  = None

while max_program_iterations == None or iterations < max_program_iterations:
    ok = True

    iterations += 1

    p = processor_z80()
    program = p.generate_program(max_program_length)

    if program == None:
        continue

    n_targets_ok = 0

    for target in targets:
        if p.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            ok = False
            break

        if p.get_accumulator() != target['result_acc']:
            ok = False
            break

        n_targets_ok += 1

    targets_ok_stat += n_targets_ok
    targets_ok_n    += 1

    if n_targets_ok > targets_ok_bestn:
        targets_ok_bestn = n_targets_ok
        targets_ok_best  = program

    if ok and (best_program == None or len(program) < len(best_program)):
        best_program    = program
        p.insert_program_init(best_program, target['initial_values'])

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

        print(f'Iterations done: {iterations}, average n_ok: {targets_ok_stat / targets_ok_n:.4f}[{targets_ok_bestn}], run time: {now - start_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second\r', end='')

# TODO: remove random instructions and check if it still works

end_ts = time.time()

print()

if best_program != None:
    diff_ts = end_ts - start_ts

    print(f'Iterations: {best_iterations}, length program: {len(best_program)}, took: {diff_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second')

    for instruction in best_program:
        print(instruction['opcode'])

else:
    print(f'Did not succeed in {iterations} iterations')
