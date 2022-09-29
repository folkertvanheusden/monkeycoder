#! /usr/bin/python3

import json

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

open('add.json', 'w').write(json.dumps(get_targets_add(), sort_keys=True, indent=4))

open('shift-1.json', 'w').write(json.dumps(get_targets_shift_1(), sort_keys=True, indent=4))

open('shift-n.json', 'w').write(json.dumps(get_targets_shift_n(), sort_keys=True, indent=4))

open('shift-loop.json', 'w').write(json.dumps(get_targets_shift_loop(), sort_keys=True, indent=4))

open('multiply.json', 'w').write(json.dumps(get_targets_multiply(), sort_keys=True, indent=4))
