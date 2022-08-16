#! /usr/bin/python3

from processor_z80 import processor_z80

def attempt_resolve(p, target_value, max_iterations):
    accumulator = p.get_accumulator()

    operations = []

    for it in range(0, max_iterations):
        operation = p.pick_operation()

        operations.append(operation)

        print(operation, p.get_register(accumulator))

        if p.get_register(accumulator) == target_value:
            break

    return operations

initialize_with = [ { 'width' : 8, 'value' : 123 },
                    { 'width' : 8, 'value' : 9 } ]

p = processor_z80(initialize_with)

print(attempt_resolve(p, 99, 1000))
