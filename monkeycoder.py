#! /usr/bin/python3

from processor import processor
from processor_z80 import processor_z80
from processor_test import processor_test
import multiprocessing
import random
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

n_processes            = max(1, multiprocessing.cpu_count() - 1)

def copy_program(program: List[dict]) -> List[dict]:
    return program[:]

# returns 0...x where 0 is perfect and x is bad
def test_program(proc, program, targets: List[dict], full: bool) -> float:
    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            print('Failed executing program')
            n_targets_ok = 0
            break

        if proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    if full:
        return 11. - (float(n_targets_ok) / len(targets) * 10 + float(len(program)) / max_program_length), program

    return 1. - float(n_targets_ok) / len(targets)

def genetic_searcher(processor_obj, targets, max_program_length, max_n_miss, stop_q, result_q):
    try:
        proc = processor_obj()

        local_best_cost = 1000000

        start = time.time()

        program = proc.generate_program(random.randint(0, max_program_length))

        work = None

        n_iterations = 0

        hit = miss = 0

        while True:
            if len(program) == 0:
                program.append(proc.pick_an_instruction())

                work = copy_program(program)

            else:
                work = copy_program(program)

                idx = random.randint(0, len(work) - 1) if len(work) > 1 else 0

                while True:
                    action = random.choice([0, 1, 2, 3])

                    if len(work) < max_program_length or action == 0 or action == 2:
                        break

                if action == 0:  # replace
                    work[idx] = proc.pick_an_instruction()

                elif action == 1:  # insert
                    work.insert(idx, proc.pick_an_instruction())

                elif action == 2:  # delete
                    work.pop(idx)

                elif action == 3:  # append
                    work.append(proc.pick_an_instruction())

                else:
                    assert False

            if len(work) > 0:
                cost = test_program(proc, work, targets, False)

                if cost <= local_best_cost:
                    if cost < local_best_cost:
                        result_q.put((n_iterations, cost, work))

                        if cost == 0:
                            break

                        n_iterations = 0

                    local_best_cost = cost

                    program = work

                    miss = 0

                    hit += 1

                else:
                    miss += 1

                    if miss >= max_n_miss:
                        miss = 0

                        random.seed()

                        program = proc.generate_program(random.randint(1, max_program_length))

                    hit   = 0

            n_iterations += 1

    except Exception as e:
        print(f'Exception: {e}, line number: {e.__traceback__.tb_lineno}')

    out_q.put(None)

if __name__ == "__main__":
    # verify if monkeycoder works
    proc = instantiate_processor_test()

    test_program_code, targets = proc.gen_test_program()

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], test_program_code) != False and proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    assert n_targets_ok == len(targets)

    targets  = [
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

    stop_q: multiprocessing.Queue = multiprocessing.Queue()
    data_q: multiprocessing.Queue = multiprocessing.Queue()

    start_ts = time.time()
    prev_now = 0

    processes = []

    for tnr in range(0, n_processes):
        proces = multiprocessing.Process(target=genetic_searcher, args=(instantiate_processor_obj, targets, max_program_length, max_n_miss, stop_q, data_q,))
        proces.start()

        processes.append(proces)

    iterations = 0

    best_program    = None
    best_cost       = 1000000
    best_iterations = None

    first_output    = True

    while True:
        result = data_q.get()

        if result is None:
            break

        iterations += result[0]

        cost        = result[1]

        program     = result[2]

        now         = time.time()

        if best_program is None or cost < best_cost or (cost == best_cost and len(program) < len(best_program)):
            best_program    = program
            best_cost       = cost
            best_iterations = iterations

            print(f'time: {time.time() - start_ts}, cost: {best_cost}, length: {len(best_program)}, iterations: {best_iterations}')

        elif cost == best_cost and now - prev_now >= 2.5:
            print(f'time: {time.time() - start_ts}, cost: {best_cost}, length: {len(best_program)}, iterations: {best_iterations}, current iterations: {iterations}')

            prev_now = now

    for proces in processes:
        stop_q.put('stop')

    for proces in processes:
        proces.join()

    n_deleted = 0

    p = instantiate_processor_obj()

    if best_program is not None:
        idx = 0

        while idx < len(best_program):
            work = copy_program(best_program)

            work.pop(idx)

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
