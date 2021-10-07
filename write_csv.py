import csv


def write_to_csv(m):
    with open('/home/pi/Desktop/budzet/paźdź.csv', 'a', encoding='UTF8', newline='') as budzet_file:
        pazdz_writer = csv.writer(budzet_file, delimiter=',')
        pazdz_writer.writerow(m.get_row())
