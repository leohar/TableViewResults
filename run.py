import os
import sys
from os import walk
import ast
import logging
import argparse
from datetime import datetime
from atlassian import Confluence

import config
import db_query
import csv_processing
import html_processing
import images_processing
import confluence_processing


def main():

    # create logging file handler
    logger = logging.getLogger("Perf_reporter")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler("perf_report.log")
    sh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(sh)

    logger.info("Reporter started")

    settings_path = 'settings.ini'
    bank_list = []
    # creating settings.ini if not exists, reading all settings
    if os.path.exists(settings_path):
        db_host = config.get_setting(settings_path, 'Settings', 'db_host')
        db_port = config.get_setting(settings_path, 'Settings', 'db_port')
        db_name = config.get_setting(settings_path, 'Settings', 'db_name')
        db_start = config.get_setting(settings_path, 'Settings', 'db_start')
        db_end = config.get_setting(settings_path, 'Settings', 'db_end')
        db_info = config.get_setting(settings_path, 'Settings', 'db_info')
        confluence_auth = (config.get_setting(settings_path, 'Settings', 'confluence_user'),
                           config.get_setting(settings_path, 'Settings', 'confluence_password'))
        confluence_url = config.get_setting(settings_path, 'Settings', 'confluence_url')
        confluence_space = config.get_setting(settings_path, 'Settings', 'confluence_space')
        confluence_page_id = config.get_setting(settings_path, 'Settings', 'confluence_page_id')
        confluence_html_to_post = config.get_setting(settings_path, 'Settings', 'confluence_html_to_post')
        confluence_path_to_post = config.get_setting(settings_path, 'Settings', 'confluence_path_to_post')
        grafana_url = config.get_setting(settings_path, 'Settings', 'grafana_url')
        garafana_dashboard_uri = config.get_setting(settings_path, 'Settings', 'garafana_dashboard_uri')
        grafana_org_id = config.get_setting(settings_path, 'Settings', 'grafana_org_id')
        grafana_panel_id_list = config.get_setting(settings_path, 'Settings', 'grafana_panel_id_list')
        grafana_panel_width = config.get_setting(settings_path, 'Settings', 'grafana_panel_width')
        grafana_panel_height = config.get_setting(settings_path, 'Settings', 'grafana_panel_height')
        logger.info(db_info)
    else:
        config.create_config('settings.ini')
        db_host = config.get_setting(settings_path, 'Settings', 'db_host')
        db_port = config.get_setting(settings_path, 'Settings', 'db_port')
        db_name = config.get_setting(settings_path, 'Settings', 'db_name')
        db_start = config.get_setting(settings_path, 'Settings', 'db_start')
        db_end = config.get_setting(settings_path, 'Settings', 'db_end')
        db_info = config.get_setting(settings_path, 'Settings', 'db_info')
        confluence_auth = (config.get_setting(settings_path, 'Settings', 'confluence_user'),
                           config.get_setting(settings_path, 'Settings', 'confluence_password'))
        confluence_url = config.get_setting(settings_path, 'Settings', 'confluence_url')
        confluence_space = config.get_setting(settings_path, 'Settings', 'confluence_space')
        confluence_page_id = config.get_setting(settings_path, 'Settings', 'confluence_page_id')
        confluence_html_to_post = config.get_setting(settings_path, 'Settings', 'confluence_html_to_post')
        confluence_path_to_post = config.get_setting(settings_path, 'Settings', 'confluence_path_to_post')
        grafana_url = config.get_setting(settings_path, 'Settings', 'grafana_url')
        garafana_dashboard_uri = config.get_setting(settings_path, 'Settings', 'garafana_dashboard_uri')
        grafana_org_id = config.get_setting(settings_path, 'Settings', 'grafana_org_id')
        grafana_panel_id_list = config.get_setting(settings_path, 'Settings', 'grafana_panel_id_list')
        grafana_panel_width = config.get_setting(settings_path, 'Settings', 'grafana_panel_width')
        grafana_panel_height = config.get_setting(settings_path, 'Settings', 'grafana_panel_height')
        logger.info(db_info)

    # command line arguments parser settings
    parser = argparse.ArgumentParser(description='Report builder requires relative template path for '
                                                 'report generation.')
    parser.add_argument(
                        "template_path",
                        metavar='1',
                        type=str,
                        help='file name or template file path')
    args = parser.parse_args()
    logger.debug(parser.parse_args())
    template_path = parser.parse_args().template_path
    db_connection_string = db_query.set_db_connection_string(host=db_host, port=db_port, name=db_name)
    logger.debug("db_connection_string = " + db_connection_string)
    test_time = db_query.set_time_string(start=db_start, end=db_end)
    logger.debug("test_time = " + test_time)
    all_bank_list = db_query.get_bank_list(db_conn=db_connection_string,
                                           test_time=test_time)
    for b in all_bank_list:
        if db_query.check_bank_query(db_conn=db_connection_string,
                                     test_time=test_time,
                                     bank=b):
            bank_list.append(b)
        else:
            continue

    logger.debug(bank_list)
    last_line_list = csv_processing.csv_read_last_line(read_path=template_path)
    csv_report_file_name = csv_processing.csv_file_name(template_path=template_path)
    html_report_file_name = html_processing.html_file_name(template_path=template_path)
    csv_headers = csv_processing.csv_read(read_path=template_path)
    csv_processing.csv_add(data=csv_headers, start_index=0, end_index=1, write_path=csv_report_file_name)

    logger.info("Start info retrieving")

    for bank in sorted(bank_list):
        service_list = []
        target_service_list = []
        found_t_service = []
        all_service_list = db_query.get_service_list(db_conn=db_connection_string,
                                                     test_time=test_time,
                                                     bank=bank)
        for s in all_service_list:
            if db_query.check_service_query(db_conn=db_connection_string,
                                            test_time=test_time,
                                            service=s,
                                            bank=bank):
                service_list.append(s)
            else:
                continue

        all_target_service_list = db_query.get_target_service_list(db_conn=db_connection_string,
                                                                   test_time=test_time,
                                                                   bank=bank)
        for ts in all_target_service_list:
            if db_query.check_target_service_query(db_conn=db_connection_string,
                                                   test_time=test_time,
                                                   t_service=ts,
                                                   bank=bank):
                target_service_list.append(ts)
            else:
                continue
        logger.debug(bank_list, service_list, target_service_list)
        for service in sorted(service_list):
            calculated_list = []
            logger.info("BANK: " + bank)
            logger.info("SERVICE: " + service)
            db_query_list = csv_processing.csv_read(read_path=template_path)
            service_result_list = db_query.query_db(db_conn=db_connection_string,
                                                    q_list=db_query_list,
                                                    service=service,
                                                    test_time=test_time)
            for target_service in sorted(target_service_list):
                if service in target_service:
                    found_t_service.append(target_service)
                    for t in found_t_service:
                        target_service_result_list = db_query.query_db_with_target_services(
                                                                                        db_conn=db_connection_string,
                                                                                        q_ts_list=last_line_list,
                                                                                        bank=bank,
                                                                                        service=service,
                                                                                        target_service=t,
                                                                                        test_time=test_time)
                        logger.debug(target_service_result_list)
                        service_result_list.append(target_service_result_list)
                        logger.debug("OVERALL RESULTS" + str(service_result_list))
                        calculated_list = process_table_data(list_to_p=service_result_list,
                                                             bank=bank,
                                                             service=service,
                                                             target_service=target_service)
                        logger.debug(calculated_list)
                    # service_result_list = []
                    found_t_service = []
            csv_processing.csv_add(data=calculated_list,
                                   start_index=1,
                                   end_index=len(calculated_list),
                                   write_path=csv_report_file_name)
            html_processing.html_add(calculated_list, html_report_file_name)
    list_for_html = csv_processing.csv_read(read_path=csv_report_file_name)
    html_processing.html_write(html_data=list_for_html, report_file_name=html_report_file_name)

    # image retrieving
    logger.info("Image retrieving started")

    time_for_url_grafana = images_processing.set_time_string(start=db_start, end=db_end)
    grafana_panel_width = ast.literal_eval(grafana_panel_width)
    grafana_panel_height = ast.literal_eval(grafana_panel_height)
    grafana_panel_id_list = grafana_panel_id_list.split(',')
    i_count = 99
    for i in range(len(grafana_panel_id_list)):
        images_processing.retrieve_pics(url=grafana_url,
                                        uri=garafana_dashboard_uri,
                                        org_id=grafana_org_id,
                                        test_time=time_for_url_grafana,
                                        id=grafana_panel_id_list[i],
                                        width=grafana_panel_width[grafana_panel_id_list[i]],
                                        height=grafana_panel_height[grafana_panel_id_list[i]],
                                        template_path=template_path,
                                        i_count=i_count)
        i_count -= 1
    logger.info("Image retrieving done!")

    # confluence posting
    confluence = Confluence(url=confluence_url, username=confluence_auth[0], password=confluence_auth[1])
    descr = os.path.splitext(template_path)[0].split('/')[1]
    test_start = db_start.strip('\'')
    test_end_time = db_end.strip('\'').split(" ")[1]
    page_title = "{} {} - {}".format(descr, test_start, test_end_time)
    files = []
    confluence.create_page(space=confluence_space,
                           title=page_title,
                           body=confluence_html_to_post,
                           parent_id=confluence_page_id)

    new_page_id = confluence.get_page_id(space=confluence_space, title=page_title)

    for (dirpath, dirnames, filenames) in walk(confluence_path_to_post):
        files.extend(filenames)
        break

    description = "<p> TEST SUMMARY" + confluence_html_to_post + "</p>"

    page_body = description

    test_duration = "<p> Test duration: " + str(datetime.strptime(db_end, "'%Y-%m-%d %H:%M:%S'") -
                                               datetime.strptime(db_start, "'%Y-%m-%d %H:%M:%S'")) + "</p>"
    page_body += test_duration

    logger.info("Start confluence report attachment")

    for file in sorted(files, reverse=True):
        if str(os.path.splitext(file)[1]) == '.png':
            response = confluence_processing.upload_attachment(auth=confluence_auth,
                                                               page_id=new_page_id,
                                                               file_path=confluence_path_to_post+file)
            base_url, filename, container_id, modification_date, attachment_id = confluence_processing.\
                get_attachments_info(response)
            image_tag = confluence_processing.prepare_html_for_image(base_url=base_url,
                                                                     filename=filename,
                                                                     container_id=container_id,
                                                                     modification_date=modification_date,
                                                                     attachment_id=attachment_id,
                                                                     height="300",
                                                                     width="825")
            image_tag = "<p>" + image_tag + "</p>"
            page_body += image_tag
        elif str(os.path.splitext(file)[1]) == '.html':
            with open(confluence_path_to_post + file, 'r') as fr:
                html_table = fr.read()
                page_body += html_table
        else:
            continue

    logger.info("Start confluence update")
    # confluence.update_page(new_page_id, title=page_title, body=page_body, minor_edit=True)
    confluence_processing.write_data_storage(auth=confluence_auth, html=page_body, page_id=new_page_id)
    logger.info("Report completed")


def process_table_data(list_to_p, bank, service, target_service):
    processed_list = list_to_p.copy()
    for r in range(len(processed_list)):
        for l in range(len(processed_list[r])):
            # print(difference_list[r][l])
            if processed_list[r][l] == "diff":
                if processed_list[r-1][l+3] == 'X' or processed_list[r+1][l] == 'X':
                    processed_list[r][l] = 'X'
                else:
                    try:
                        processed_list[r][l] = int(processed_list[r-1][l+3]) - int(processed_list[r+1][l])
                    except ValueError:
                        processed_list[r][l] = '-'
            elif processed_list[r][l] == "bank":
                processed_list[r][l] = bank
            elif processed_list[r][l] == "service":
                processed_list[r][l] = service
            elif processed_list[r][l] == "target_service":
                processed_list[r][l] = target_service
            else:
                continue
            # print("difference list")
            # print(difference_list)
    return processed_list


if __name__ == "__main__":
    main()
