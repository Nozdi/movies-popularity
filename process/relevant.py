#!/usr/bin/env python
"""
Tool to get just relevant data from csv
"""
import csv
import re
from datetime import datetime

FROM = datetime(2015, 2, 1)
TO = datetime(2015, 5, 1)


def process(original_filename, new_filename):
    with open(original_filename, 'rb') as ofp, open(new_filename, 'wb') as nfp:
        reader = csv.reader(ofp)
        writer = csv.writer(nfp)
        for row in reader:
            try:
                if FROM <= datetime.strptime(row[0], "%B %d %Y") < TO:
                    row[1] = re.sub(r"\(\w+\)", '', row[1])  # removing parenthesis
                    writer.writerow(row[:-1])  # removing trailer
            except ValueError:
                continue


if __name__ == '__main__':
    process("repaired.csv", "relevant.csv")
