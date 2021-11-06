import csv
import os
from pathlib import Path

from const import INPUT_CSV, HISTORY_CSV


def write_to_input(m):
    with open(INPUT_CSV, 'w', encoding='UTF8', newline='') as budget_file:
        input_writer = csv.writer(budget_file, delimiter=',')
        input_writer.writerow(['KIEDY', 'CO', 'KTO', 'ILE', 'MAILE'])
        input_writer.writerow(m.get_row())


def write_to_history(m):
    with open(HISTORY_CSV, 'a', encoding='UTF8', newline='') as history_file:
        history_writer = csv.writer(history_file, delimiter=',')
        history_writer.writerow(m.get_row_with_category())


def delete_file():
    input_file = Path(INPUT_CSV)
    if input_file.is_file():
        os.remove(INPUT_CSV)
