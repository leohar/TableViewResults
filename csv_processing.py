import logging
import csv
import sys
import os


module_logger = logging.getLogger("Perf_reporter.csv_processing")


def csv_file_name(template_path):
    logger = logging.getLogger("Perf_reporter.csv_processing.csv_file_name")
    csv_report_path = 'report_files/' + str(os.path.splitext(template_path)[0].split('/')[1]) + '_report' + os.path.splitext(template_path)[1]
    logger.debug(os.path.splitext(template_path)[0].split('/')[1])
    logger.debug(os.path.splitext(template_path)[1])
    return csv_report_path


def csv_read(read_path):

    query_list = []
    """
    Read a csv file
    """
    try:
        with open(read_path, "r") as in_file:
            reader = csv.reader(in_file, delimiter=';')
            # print(list(reader))
            for row in reader:
                query_list.append(row)
            # deleting last line which is reserved for target_services querry
            del query_list[-1]
            return query_list
    except OSError as e:
        print(e)
        sys.exit("Error reading template, check file path")


def csv_read_last_line(read_path):

    try:
        with open(read_path, "r") as in_file:
            last_line = in_file.readlines()[-1].split(";")
            # print("__________________________________________LAST_LINE_______________________________________________")
            # print(last_line)
            return last_line
    except OSError as e:
        print(e)
        sys.exit("Error reading template, check file path")


def csv_read_first_line(read_path):

    try:
        with open(read_path, "r") as in_file:
            first_line = in_file.readlines()[0].split(";")
            # print("__________________________________________FIRST_LINE______________________________________________")
            # print(last_line)
            return first_line
    except OSError as e:
        print(e)
        sys.exit("Error reading template, check file path")


def csv_write(data, write_path):
    """
    Пишем в CSV
    """
    try:
        with open(write_path, "w", newline='') as out_file:
            writer = csv.writer(out_file, delimiter=';')
            for row in data:
                # print('write')
                # print(line)
                writer.writerow(row)
        logger = logging.getLogger("Perf_reporter.csv_processing.csv_write")
        logger.info('Отчет в формате csv создан: ' + write_path)
    except OSError as e:
        print(e)


def csv_add(data, start_index, end_index, write_path):
        """
        Пишем в CSV
        """
        try:
            with open(write_path, "a", newline='') as out_file:
                writer = csv.writer(out_file, delimiter=';')
                for row in range(start_index, end_index):
                    # print('write')
                    # print(line)
                    writer.writerow(data[row])
            logger = logging.getLogger("Perf_reporter.csv_processing.csv_add")
            logger.info('Added to: ' + write_path)
        except OSError as e:
            print(e)

