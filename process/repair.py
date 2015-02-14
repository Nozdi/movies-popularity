#!/usr/bin/env python
"""
Tool to repair csv generated from html
"""

from __future__ import print_function
import fileinput

if __name__ == '__main__':
    year = ''
    for line in fileinput.input():
        if line.strip() == "":
            continue
        elif line.startswith('"'):
            year = line.strip('"\r\n').split()[-1]
        elif not line.startswith(','):
            splitted = line.split(',')
            previous = "{} {}".format(
                splitted[0],
                year,
            )
            print(",".join([previous] + splitted[1:]), end='')
        else:
            print(previous + line, end='')
