from datetime import datetime, timedelta
from urllib.request import urlretrieve
import calendar
import requests
import logging
import os


module_logger = logging.getLogger("Perf_reporter.images_processing")


def image_file_name(template_path, i_count):
    image_path = 'report_files/{}_'.format(i_count) + os.path.splitext(template_path)[0].split('/')[1] + '_image.png'
    return image_path


def set_time_string(start, end):
    logger = logging.getLogger("Perf_reporter.images_processing.set_time_string")
    logger.debug(start)
    logger.debug(end)
    start = (datetime.strptime(start, "'%Y-%m-%d %H:%M:%S'") - timedelta(hours=4)).strftime("'%Y-%m-%dT%H:%M:%SZ'")
    end = (datetime.strptime(end, "'%Y-%m-%d %H:%M:%S'") - timedelta(hours=4)).strftime("'%Y-%m-%dT%H:%M:%SZ'")
    time_str = "from={}&to={}".format(utc_time_to_epoch(start), utc_time_to_epoch(end))
    return time_str


def utc_time_to_epoch(timestamp_string):
    timestamp = datetime.strptime(timestamp_string, "'%Y-%m-%dT%H:%M:%SZ'")
    epoch = (calendar.timegm(timestamp.utctimetuple())*1000)
    return epoch


def retrieve_pics(url, uri, org_id, test_time, id, width, height, template_path, i_count):
    logger = logging.getLogger("Perf_reporter.images_processing.retrieve_pics")
    request_str = "{}{}?orgId={}&{}&panelId={}&width={}&height={}".format(url,
                                                                          uri,
                                                                          org_id,
                                                                          test_time,
                                                                          id,
                                                                          width,
                                                                          height)

    logger.info(request_str)
    # #### VAR I
    #
    # urlretrieve(request_str, image_file_name(template_path, id))

    # ### VAR II
    response = requests.get(request_str, auth=('admin', 'admin'))
    if response.status_code == 200:
        with open(image_file_name(template_path, i_count), 'wb') as out_file:
            out_file.write(response.content)
    else:
        logger.info(response.status_code)
        logger.info(response.text)
    del response
