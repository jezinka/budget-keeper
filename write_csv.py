import csv
import os


def write_to_input(m):
    with open('data/input.csv', 'w', encoding='UTF8', newline='') as budget_file:
        input_writer = csv.writer(budget_file, delimiter=',')
        input_writer.writerow(['KIEDY', 'CO', 'KTO', 'ILE', 'MAILE'])
        input_writer.writerow(m.get_row())


def write_to_history(m):
    with open('data/history.csv', 'a', encoding='UTF8', newline='') as history_file:
        history_writer = csv.writer(history_file, delimiter=',')
        history_writer.writerow(m.get_row_with_category())


def delete_file():
    os.remove('data/input.csv')
