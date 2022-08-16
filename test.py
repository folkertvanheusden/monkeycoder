#! /usr/bin/python3

from processor_z80 import processor_z80

def attempt_resolve(p, target_value, max_iterations):
    accumulator = p.get_accumulator()

    operations = []

    for it in range(0, max_iterations):
        operation = p.pick_operation()

        operations.append(operation)

        if p.get_register(accumulator)['value'] == target_value:
            return operations

    return None

initialize_with  = [ { 'width' : 8, 'value' : 123 },
                     { 'width' : 8, 'value' : 9 } ]

acc_target_value = 99  # accumulator target value

max_program_iterations = 1000
max_program_length     = 1024

iterations   = 0

best_program    = None
best_iterations = None

while iterations < max_program_iterations:
    p = processor_z80(initialize_with)

    program = attempt_resolve(p, acc_target_value, max_program_length)

    iterations += 1

    if program != None and (best_program == None or len(program) < len(best_program)):
        best_program    = program
        best_iterations = iterations

print(f'Iterations: {best_iterations}')

print(best_program)
