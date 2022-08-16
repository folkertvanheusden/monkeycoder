#! /usr/bin/python3

from processor_z80 import processor_z80
import time

targets  = [
            { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                  { 'width' : 8, 'value' : 1   } ],
              'result_acc': 2 },
            { 'initial_values': [ { 'width' : 8, 'value' : 2 },
                                  { 'width' : 8, 'value' : 1   } ],
              'result_acc': 3 },
            { 'initial_values': [ { 'width' : 8, 'value' : 1 },
                                  { 'width' : 8, 'value' : 2   } ],
              'result_acc': 3 },
    ]

max_program_iterations = 30000
max_program_length     = 1024

iterations = 0

start_ts   = time.time()

best_program    = None
best_iterations = None

while iterations < max_program_iterations:
    ok = True

    iterations += 1

    p = processor_z80()
    program = p.generate_program(max_program_length)

    if program == None:
        continue

    for target in targets:
        if p.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            ok = False
            break

        if p.get_accumulator() != target['result_acc']:
            ok = False
            break

    if ok and (best_program == None or len(program) < len(best_program)):
        best_program    = program
        p.insert_program_init(best_program, target['initial_values'])

        best_iterations = iterations

# TODO: remove random instructions and check if it still works

end_ts = time.time()

if best_program != None:
    diff_ts = end_ts - start_ts

    print(f'Iterations: {best_iterations}, length program: {len(best_program)}, took: {diff_ts:.2f} seconds, {max_program_iterations / diff_ts:.2f} iterations per second')

    for instruction in best_program:
        print(instruction['opcode'])

else:
    print(f'Did not succeed in {iterations} iterations')
