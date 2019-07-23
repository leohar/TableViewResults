import os
import config
import configparser
import requests
import json
import csv
import sys
import argparse

from prettytable import PrettyTable
from prettytable import DEFAULT

# import fileinput
# from pandas import read_csv
# import jq

# with open(infile, "w", encoding="utf-8") as file_json:
#     file_json.write(json_data)
#     file_json.close()
#
# html_data = json2html.convert(json = json_data, clubbing = False)
# print(html_data)
#
# with open(outfile,"w", encoding="utf-8") as html_file:
#     html_file.write(html_data)
#     html_file.close()
#     os.system(outfile)

def create_db_connection_string(host, port, name):
    db_connection_str = "http://{}:{}/query?db={}".format(host, port, name)
    return db_connection_str

def query_db(db_conn, query_list, test_time):
    print(query_list)
    print(list(query_list))
    result_list = query_list.copy()
    difference_needed = False
    # print(result_list)
    for i in range(len(query_list)):
        for j in range(len(query_list[i])):
            # print(query_list[i][j], end=' ')
            # print("dbconn = " + db_conn)
            q = query_list[i][j]
            query_str = "q={}&{}".format(q, test_time)
            print("query_str = "+ query_str)
            r = requests.get(db_conn, query_str)
            if r.status_code == 200:
                print("HTTP CODE: ", r.status_code)
                json_data = r.json()
                # print(json_data)
                # print(json_data['results'][0]['series'][0]['values'][0][1])
                res_int = int(json_data['results'][0]['series'][0]['values'][0][1])  # округляем float до int
                # print(result_list[i][j])
                result_list[i][j] = res_int.__str__()
                if (difference_needed == True):
                    result_list[i][j - 1] = difference(diff_base, res_int)
                    difference_needed = False
                else:
                    continue
                print()
            elif r.status_code != 200 and q == "ems":
                print("HTTP CODE: ", r.status_code)
                # print("before " + difference_needed.__str__())
                difference_needed = True
                diff_base = res_int
                # print("after " + difference_needed.__str__())
            else:
                print("HTTP CODE: ", r.status_code)
                # raise Exception()
                # result_list[i][j] = q
            # print("result list")
            # print(result_list)
    return result_list

def csv_read(read_path):
    """
    Read a csv file
    """
    try:
        with open(read_path, "r") as f_obj:
            reader = csv.reader(f_obj, delimiter=';')
            # print(list(reader))
            for row in reader:
                db_query_list.append(row)
        return db_query_list
    except OSError as e:
        print(e)
        sys.exit("Ошибки в чтении темплейта, проверьте путь к файлу")

def csv_write(data, write_path):
    """
    Пишем в CSV
    """
    report_file_name = os.path.splitext(write_path)[0] + '_report' + os.path.splitext(write_path)[1]
    try:
        with open(report_file_name, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            for line in data:
                # print('write')
                # print(line)
                writer.writerow(line)
        print('Отчет в формате csv создан: ' + report_file_name)
    except OSError as e:
        print(e)

def html_write(html_data, html_write_path):
    """
        Пишем в html
    """
    report_file_name = os.path.splitext(html_write_path)[0] + '_report.html'
    # print(html_data[0])
    x = PrettyTable(border=True, header=False, padding_width=3)
    # count = 0
    # for i in html_data[0]:
    #         x.field_names.append(count.__str__())
    #         count += 1

    # print("field names")
    # print(x.field_names)

    for j in range(len(html_data)):
        splited_row = html_data[j]
        # print(html_data[i])
        x.add_row(splited_row)
        # x.print_html(attributes={"border": "1"})
    # x.print_html(attributes={"border": "1"})
    print(x)
    html_code = x.get_html_string(format=True)
    try:
        with open(report_file_name, "w") as html_file:
            html_file = html_file.write(html_code)
        print('Отчет в формате html создан: ' + report_file_name)
    except OSError as e:
        print(e)

def set_date(start, end):
    test_time = "from={}&to{}".format(start, end)
    return test_time

def difference(a,b):
    try:
        return a - b
    except:
        ArithmeticError

if __name__ == "__main__":

    settings_path = 'settings.ini'
    # создаем, если нет дефолтный файл настроек, считываем подключение к базе
    if os.path.exists(settings_path):
        db_host = config.get_setting(settings_path, 'Settings', 'db_host')
        db_port = config.get_setting(settings_path, 'Settings', 'db_port')
        db_name = config.get_setting(settings_path, 'Settings', 'db_name')
        db_info = config.get_setting(settings_path, 'Settings', 'db_info')
        print(db_info)
    else:
        config.create_config('settings.ini')
        print(db_info)
    # Раскомментировать ниже, если ничего не передано в коммандной строке
    # - время в формате Unix https://www.epochconverter.com/ либо 'now() - 7d'
    # test_start = '1562668594441'
    # test_end = '1562672194442'

    # - пути темплейтов и результирующих файлов
    # template_path = "templates/test.csv"
    # results_path = "results/test.csv"

    db_query_list = []
    result_list = []

    # настройки парсера аргументов коммандной строки
    parser = argparse.ArgumentParser(description='Report builder requires parameters listed under for report generation.')
    parser.add_argument('c_template_path',
                        metavar='1',
                        type=str,
                        help='a name or template file path')
    parser.add_argument('c_test_start',
                        metavar='2',
                        type=str,
                        default='now-1h',
                        help='time in Unix format from Grafana URL, parameter &from=')
    parser.add_argument('c_test_end',
                        metavar='3',
                        type=str,
                        default='now',
                        help='time in Unix format from Grafana URL, parameter &to=')

    args = parser.parse_args()
    # print(parser.parse_args())

    test_start = parser.parse_args().c_test_start
    test_end = parser.parse_args().c_test_end
    template_path = parser.parse_args().c_template_path

    db_connection_string = create_db_connection_string(db_host, db_port, db_name)
    # print("db_connection_string = " + db_connection_string)
    test_time = set_date(test_start, test_end)
    # print("test_time = " + test_time)
    csv_read(template_path)
    result_list = query_db(db_connection_string, db_query_list, test_time)
    csv_write(result_list, template_path)
    html_write(result_list, template_path)