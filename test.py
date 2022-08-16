#! /usr/bin/python3

from processor_z80 import processor_z80

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

acc_target_value = 99  # accumulator target value

max_program_iterations = 1000
max_program_length     = 1024

iterations   = 0

best_program    = None
best_iterations = None

while iterations < max_program_iterations:
    ok = True

    p = processor_z80()
    program = p.generate_program()

    accumulator = p.get_accumulator()

    for target in targets:
        if p.execute_program(target) == False:  # False: in case an execution error occured
            ok = False
            break

        if p.get_register(accumulator)['value'] != target_value:
            ok = False
            break

    iterations += 1

    if ok and (best_program == None or len(program) < len(best_program)):
        best_program    = program
        best_iterations = iterations

print(f'Iterations: {best_iterations}')

print(best_program)
