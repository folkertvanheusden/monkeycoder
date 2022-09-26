#! /usr/bin/python3

from processor import processor
from processor_z80 import processor_z80
from processor_test import processor_test
import copy
import logging
import multiprocessing
import os
import queue
import random
import sys
import time
from typing import Any, List, Tuple

def instantiate_processor_z80():
    return processor_z80()

def instantiate_processor_test():
    return processor_test()

instantiate_processor_obj = instantiate_processor_z80

max_program_iterations = None
max_program_length     = 512
max_n_miss             = max_program_length * 4  # 4 operation types (replace, append, delete, insert)

n_processes            = multiprocessing.cpu_count()

def emit_program(best_program):
    tmp_file = '__.tmp.dat.-'

    fh = open(tmp_file, 'w')
    for line in best_program:
        if 'label' in line:
            fh.write(f'{line["label"] + ":":8s} {line["opcode"]}\n')

        else:
            fh.write(f'          {line["opcode"]}\n')

    fh.close()

    os.rename(tmp_file, 'current.asm')

# returns 0...x where 0 is perfect and x is bad
def test_program(proc: processor, program: List[dict], targets: List[dict], full: bool) -> Tuple[float, bool]:
    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], program) == False:  # False: in case an execution error occured
            logging.error('Failed executing program')
            n_targets_ok = 0
            sys.exit(1)
            break

        if proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    all_ok = n_targets_ok == len(targets)

    if full:
        mul = 1 / len(targets)

        return 21. - (float(n_targets_ok) * mul * 10 - float(len(program)) / max_program_length * mul + all_ok * 10), all_ok

    return 2. - (float(n_targets_ok) / len(targets) + all_ok), all_ok

def genetic_searcher(processor_obj, targets, max_program_length: int, max_n_miss: int, cmd_q, result_q):
    try:
        local_best_cost = 1000000.

        local_best_prog = None

        local_best_ok   = False

        proc         = processor_obj()

        start        = time.time()

        random.seed()

        program_meta = proc.generate_program(random.randint(1, max_program_length))

        work         = None

        n_iterations = 0

        n_regenerate = 0

        miss         = 0

        while True:
            try:
                cmd = cmd_q.get_nowait()

                if cmd == 'results':
                    result_q.put((n_iterations, local_best_cost, local_best_prog, local_best_ok, n_regenerate))

                    n_iterations = 0

                    n_regenerate = 0

                elif cmd == 'stop':
                    break

            except Exception as e:
                pass

            work_meta = copy.deepcopy(program_meta)

            work      = work_meta['code']

            n_actions = random.randint(1, 8)

            for i in range(0, n_actions):
                len_work = len(work)

                idx      = random.randint(0, len_work - 1) if len_work > 1 else 0

                if len_work == 0:
                    action = 3

                elif len_work >= max_program_length:
                    action = random.choice([0, 2, 4])

                else:
                    action = random.choice([0, 1, 2, 3, 4])

                if action == 0:  # replace
                    work.pop(idx)

                    for instruction in reversed(proc.pick_an_instruction(work_meta, len(work) + 1)):
                        work.insert(idx, instruction)

                elif action == 1:  # insert
                    for instruction in reversed(proc.pick_an_instruction(work_meta, len(work) + 1)):
                        work.insert(idx, instruction)

                elif action == 2:  # delete
                    work.pop(idx)

                elif action == 3:  # append
                    for instruction in proc.pick_an_instruction(work_meta, len(work) + 1):
                        work.append(instruction)

                elif action == 4:  # swap
                    idx2 = random.randint(0, len_work - 1) if len_work > 1 else 0

                    if idx != idx2:
                        work[idx], work[idx2] = work[idx2], work[idx]

                else:
                    assert False

            if len(work) > 0:
                line_map = processor.generate_line_map(work)

                i = 0

                while i < len(work):
                    if 'destination_label' in work[i] and not work[i]['destination_label'] in line_map:
                        work.pop(i)

                    else:
                        i += 1

            if len(work) > 0:
                cost, ok = test_program(proc, work, targets, True)
                
                if cost <= local_best_cost:
                    local_best_cost = cost
                    local_best_prog = copy.deepcopy(work)
                    local_best_ok   = ok

                    program_meta    = copy.deepcopy(work_meta)

                    miss            = 0

                else:
                    miss           += 1

                    if miss >= max_n_miss:
                        miss         = 0

                        random.seed()

                        program_meta = proc.generate_program(random.randint(1, max_program_length))

                        n_regenerate += 1

            n_iterations += 1

    except Exception as e:
        logging.error(f'Exception: {e}, line number: {e.__traceback__.tb_lineno}')

    logging.info('Process is terminating...')

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

def clean_labels(code):
    labels_used = set()

    n_branches = 0

    for instruction in code:
        if instruction['instruction'] in [ processor.Instruction.i_jump_c, processor.Instruction.i_jump_nc, processor.Instruction.i_jump_z, processor.Instruction.i_jump_nz ]:
            labels_used.add(instruction['destination_label'])

            n_branches += 1

    logging.debug(f'Used {len(labels_used)} labels in {n_branches} branches')

    n_removed = 0

    for instruction in code:
        if 'label' in instruction and not instruction['label'] in labels_used:
            del instruction['label']

            n_removed += 1

    logging.debug(f'Removed {n_removed} obsolete labels')

if __name__ == "__main__":
    logging.basicConfig(filename='monkeycoder.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(asctime)s %(levelname)s:\t%(message)s'))
    logging.getLogger('').addHandler(console)

    logging.info(f'Number of processes: {n_processes}')

    # verify if monkeycoder works
    logging.info('Verify...')
    proc = instantiate_processor_test()

    test_program_code, targets = proc.generate_test_program()

    n_targets_ok = 0

    for target in targets:
        if proc.execute_program(target['initial_values'], test_program_code) != False and proc.get_accumulator() == target['result_acc']:
            n_targets_ok += 1

    assert n_targets_ok == len(targets)

    logging.info('Go!')
    targets = get_targets_shift_loop()

    result_q: queue.Queue[Any] = multiprocessing.Manager().Queue()

    prev_now = 0

    start_ts = time.time()

    processes = []
    cmd_qs    = []

    for tnr in range(0, n_processes):
        cmd_q: queue.Queue[Any] = multiprocessing.Manager().Queue()
        cmd_qs.append(cmd_q)

        proces = multiprocessing.Process(target=genetic_searcher, args=(instantiate_processor_obj, targets, max_program_length, max_n_miss, cmd_q, result_q,))
        proces.start()

        processes.append(proces)

    iterations      = 0

    n_regenerate    = 0

    best_program    = None
    best_cost       = 1000000
    best_iterations = None

    first_output    = True

    prev_ts         = time.time()

    while True:
        one_ok      = False

        any_change  = False

        batch_it    = 0
        b_n_regen   = 0

        for q in cmd_qs:
            q.put('results')

            result        = result_q.get()

            batch_it     += result[0]

            cost          = result[1]

            program       = result[2]

            if program is None:
                continue

            ok            = result[3]

            b_n_regen    += result[4]

            now           = time.time()

            one_ok |= ok

            write_file = False

            if best_program is None or cost < best_cost:
                best_program    = program
                best_cost       = cost
                best_iterations = iterations

                write_file      = True

                any_change = True

            elif cost == best_cost:
                if len(program) < len(best_program):
                    best_program    = program
                    best_iterations = iterations

                    any_change = True

                    write_file = True

            if write_file:
                emit_program(best_program)

        iterations   += batch_it

        n_regenerate += b_n_regen

        now    = time.time()
        t_diff = now - start_ts
        i_s    = iterations / t_diff

        if best_program != None:
            logging.info(f'dt: {t_diff:6.3f}, cost: {best_cost:.6f}, length: {len(best_program):3d}, #it: {best_iterations}, cur.#it: {iterations}, i/s: {i_s:.2f}, cur i/s: {batch_it / (now - prev_ts):.2f}, ok: {one_ok}, #regen: {b_n_regen}')

        if any_change == False and one_ok == True:
            break

        prev_ts = now

        time.sleep(5)

    end_ts = time.time()

    clean_labels(best_program)

    proc = instantiate_processor_obj()

    best_program = proc.get_program_init(targets[0]['initial_values']) + best_program

    if best_program is not None:
        diff_ts = end_ts - start_ts

        logging.info(f'Iterations: {best_iterations}, length program: {len(best_program)}, took: {diff_ts:.2f} seconds, {iterations / diff_ts:.2f} iterations per second')

        emit_program(best_program)

        for instruction in best_program:
            logging.info(instruction['opcode'])

    else:
        logging.info(f'Did not succeed in {iterations} iterations')

    logging.info('Finishing processes...')

    for q in cmd_qs:
        q.put('stop')

    logging.info(f'Wait for {len(processes)} processes to stop...')

    for p in processes:
        p.join()

    logging.info('Bye')
