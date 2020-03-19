from prettytable import *
import logging
import os


module_logger = logging.getLogger("Perf_reporter.html_processing")


def html_file_name(template_path):
    html_report_path = 'report_files/' + os.path.splitext(template_path)[0].split('/')[1] + '_report.html'
    return html_report_path


def html_write(html_data, report_file_name):
    """
        Пишем в html
    """
    logger = logging.getLogger("Perf_reporter.html_processing.html_write")
    x = PrettyTable(border=False, header=True, hrules=NONE, vrules=NONE, padding_width=2)
    for h in html_data[0]:
        logger.debug(h)
        x.field_names.append(h)
    # for r in range(1, len(html_data)):
    #     splitted_row = html_data[r]
    #     x.add_row(splitted_row)
    #     # x.print_html(attributes={"border": "1"})
    # # logger.debug(x)
    for r in range(1, len(html_data)):
        splitted_row = html_data[r]
        x.add_row(splitted_row)
    html_code = x.get_html_string(format=False)
    try:
        with open(report_file_name, "w") as out_file:
            html_file = out_file.write(html_code)
        logger.info('HTML report created: ' + report_file_name)
    except OSError as e:
        print(e)


def html_add(html_data, report_file_name):
    """
        Пишем в html
    """
    logger = logging.getLogger("Perf_reporter.html_processing.html_add")
    # logger.debug(html_data[0])
    x = PrettyTable(border=True, header=False, padding_width=3)
    # count = 0
    # for i in html_data[0]:
    #         x.field_names.append(count.__str__())
    #         count += 1
    # logger.debug("field names")
    # logger.debug(x.field_names)
    for j in range(1, len(html_data)):
        splitted_row = html_data[j]
        x.add_row(splitted_row)
        # x.print_html(attributes={"border": "1"})
    logger.info(x)
    html_code = x.get_html_string(format=True)

    try:
        with open(report_file_name, "a") as out_file:
            html_file = out_file.write(html_code)
        logger.info('Added to: ' + report_file_name)
    except OSError as e:
        print(e)
