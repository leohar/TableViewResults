from datetime import datetime, timedelta
import logging
import requests
import json


module_logger = logging.getLogger("Perf_reporter.db_query")


def set_db_connection_string(host, port, name):
    db_connection_str = "http://{}:{}/query?db={}&precission=s".format(host, port, name)
    return db_connection_str


def set_time_string(start, end):

    utc_from = (datetime.strptime(start, "'%Y-%m-%d %H:%M:%S'") - timedelta(hours=4)).strftime("'%Y-%m-%dT%H:%M:%SZ'")
    utc_to = (datetime.strptime(end, "'%Y-%m-%d %H:%M:%S'") - timedelta(hours=4)).strftime("'%Y-%m-%dT%H:%M:%SZ'")

    time_string = "time >= {} AND time <= {}".format(utc_from, utc_to)
    # time_string = "from={}&to={}".format(from_epoch, to_epoch) # unix time i URL
    # time_string = "time > {}() - {}".format(from_epoch, to_epoch)  # relative time
    return time_string


def get_bank_list(db_conn, test_time):
    logger = logging.getLogger("Perf_reporter.db_query.get_bank_list")
    res_banks = set()

    bank_query = 'SHOW TAG VALUES WITH KEY="ORG_ID"'
    query_str = 'q={} WHERE {}'.format(bank_query, test_time)
    logger.debug("query_str = " + str(query_str))
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        rs = json.loads(r.text)
        logger.debug(rs)
        series = rs["results"][0]['series'][0]['values']
        logger.debug(series)
        for v in series:
            res_banks.add(v[1])
    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()
    banks = list(res_banks)
    # sorted(banks)
    logger.debug(banks)
    return banks


def get_service_list(db_conn, test_time, bank):
    logger = logging.getLogger("Perf_reporter.db_query.get_service_list")
    res_services = set()

    bank_query = 'SHOW TAG VALUES WITH KEY="SERVICE_TYPE"'
    query_str = 'q={} WHERE ({} AND "ORG_ID"=\'{}\')'.format(bank_query, test_time, bank)
    logger.debug("query_str = " + query_str)
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        rs = json.loads(r.text)
        logger.debug(rs)
        # print(rs)
        series = rs["results"][0]['series'][0]['values']
        # print(series)
        for v in series:
            res_services.add(v[1])
    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()
    services = list(res_services)
    logger.debug(services)
    return services


def get_target_service_list(db_conn, test_time, bank):
    logger = logging.getLogger("Perf_reporter.db_query.get_target_service_list")
    res_target_services = set()

    bank_query = 'SHOW TAG VALUES WITH KEY="TARGET_SYSTEM_SERVICE"'
    query_str = 'q={} WHERE ({} AND "ORG_ID"=\'{}\')'.format(bank_query, test_time, bank)
    logger.debug("query_str = " + query_str)
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        rs = json.loads(r.text)
        logger.debug(rs)
        # print(rs)
        series = rs["results"][0]['series'][0]['values']
        # print(series)
        for v in series:
            res_target_services.add(v[1])  # .replace("_Call", "")

    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()
    target_services = list(res_target_services)
    logger.debug(target_services)
    return target_services


def check_bank_query(db_conn, test_time, bank):
    logger = logging.getLogger("Perf_reporter.db_query.check_bank_query")

    bank_query = 'SELECT MEAN("METRIC_VALUE") FROM "tibco_stats_jerome_API"'
    query_str = 'q={} WHERE ({} AND "ORG_ID"=\'{}\')'.format(bank_query, test_time, bank)
    logger.debug("query_str = " + str(query_str))
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        try:
            rs = json.loads(r.text)
            logger.debug(rs)
            series = rs["results"][0]['series'][0]['values'][0][1]
            logger.debug(series)
            if series != 0:
                return True
            else:
                return False
        except KeyError:
            return False
    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()


def check_service_query(db_conn, test_time, service, bank):
    logger = logging.getLogger("Perf_reporter.db_query.check_service_query")

    query = 'SELECT MEAN("METRIC_VALUE") FROM "tibco_stats_jerome_API"'
    query_str = 'q={} WHERE ({} AND "SERVICE_TYPE"=\'{}\' AND "ORG_ID" = \'{}\')'.format(query, test_time, service, bank)
    logger.debug("query_str = " + str(query_str))
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        try:
            rs = json.loads(r.text)
            logger.debug(rs)
            series = rs["results"][0]['series'][0]['values'][0][1]
            logger.debug(series)
            if series != 0:
                return True
            else:
                return False
        except KeyError:
            return False
    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()


def check_target_service_query(db_conn, test_time, t_service, bank):
    logger = logging.getLogger("Perf_reporter.db_query.check_target_service_query")

    query = 'SELECT MEAN("METRIC_VALUE") FROM "tibco_stats_jerome_API"'
    query_str = 'q={} WHERE ({} AND "TARGET_SYSTEM_SERVICE" = \'{}\' AND "ORG_ID" = \'{}\')'.format(query, test_time, t_service, bank)
    logger.debug("query_str = " + str(query_str))
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        try:
            rs = json.loads(r.text)
            logger.debug(rs)
            series = rs["results"][0]['series'][0]['values'][0][1]
            logger.debug(series)
            if series != 0:
                return True
            else:
                return False
        except KeyError:
            return False
    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()


def check_query(db_conn, test_time, bank, **kwargs):
    logger = logging.getLogger("Perf_reporter.db_query.check_target_service_query")
    service = ' AND "SERVICE_TYPE" = \'{}\''.format(kwargs.get('service'))
    t_service = ' AND "TARGET_SYSTEM_SERVICE" = \'{}\''.format(kwargs.get('t_service'))
    query = 'SELECT MEAN("METRIC_VALUE") FROM "tibco_stats_jerome_API"'
    query_str = 'q={} WHERE ({} AND "ORG_ID" = \'{}\'{}{})'.format(query, test_time, bank, service, t_service)
    logger.debug("query_str = " + str(query_str))
    r = requests.get(db_conn, query_str)
    if r.status_code == 200:
        # print("HTTP CODE: ", r.status_code)
        # print(r.text)
        try:
            rs = json.loads(r.text)
            logger.debug(rs)
            series = rs["results"][0]['series'][0]['values'][0][1]
            logger.debug(series)
            if series != 0:
                return True
            else:
                return False
        except KeyError:
            return False
    else:
        print("HTTP CODE: ", r.status_code)
        print(r.text)
        raise Exception()


def query_db(db_conn, q_list, service, test_time):

    logger = logging.getLogger("Perf_reporter.db_query.query_db")
    logger.debug(list(q_list))
    result_list = q_list.copy()
    for i in range(len(q_list)):
        for j in range(len(q_list[i])):
            logger.debug("db_conn = " + str(db_conn))
            q = q_list[i][j]
            query_str = "q={} AND" \
                        " \"SERVICE_TYPE\" = '{}' AND {})".format(q, service, test_time)
            logger.debug("query_str = " + query_str)
            r = requests.get(db_conn, query_str)
            if r.status_code == 200 and r.text == '{"results":[{"statement_id":0}]}':
                result_list[i][j] = '0'
            elif r.status_code == 200:
                logger.debug("HTTP CODE: ", r.status_code)
                logger.debug(r.text)
                try:
                    # json_data = r.json()
                    rs = json.loads(r.text)
                    series = rs["results"][0]['series'][0]
                    res_avg = int(series['values'][0][1])
                    logger.debug(rs['results'][0]['series'][0]['values'][0][1])
                    # res_avg = int(rs['results'][0]['series'][0]['values'][0][1])  # округляем float до int
                    result_list[i][j] = res_avg.__str__()
                except KeyError:
                    result_list[i][j] = 'X'
            else:
                logger.debug("HTTP CODE: ", r.status_code)
                logger.debug(r.text)
                logger.debug("results_list ")
                logger.debug(result_list)
                continue
                # raise Exception()
    return result_list


def query_db_old(db_conn, q_list, bank, service, test_time):

    logger = logging.getLogger("Perf_reporter.db_query.query_db")
    logger.debug(list(q_list))
    result_list = q_list.copy()
    for i in range(len(q_list)):
        for j in range(len(q_list[i])):
            logger.debug("db_conn = " + str(db_conn))
            q = q_list[i][j]
            query_str = "q={} AND \"ORG_ID\" = '{}' AND" \
                        " \"SERVICE_TYPE\" = '{}' AND {})".format(q, bank, service, test_time)
            logger.debug("query_str = " + query_str)
            r = requests.get(db_conn, query_str)
            if r.status_code == 200:
                logger.debug("HTTP CODE: ", r.status_code)
                logger.debug(r.text)
                try:
                    # json_data = r.json()
                    rs = json.loads(r.text)
                    series = rs["results"][0]['series'][0]
                    res_avg = int(series['values'][0][1])
                    if res_avg is None:
                        result_list[i][j] = 'none'
                    else:
                        logger.debug(rs['results'][0]['series'][0]['values'][0][1])
                        # res_avg = int(rs['results'][0]['series'][0]['values'][0][1])  # округляем float до int
                    result_list[i][j] = res_avg.__str__()
                except KeyError:
                    continue
                    # result_list[i][j] = 'X'
            else:
                logger.debug("HTTP CODE: ", r.status_code)
                logger.debug(r.text)
                logger.debug("results_list ")
                logger.debug(result_list)
                continue
                # raise Exception()
    return result_list


def query_db_with_target_services(db_conn, q_ts_list, bank, service, target_service, test_time):

    logger = logging.getLogger("Perf_reporter.db_query.query_db_with_target_services")
    logger.debug("__________________________________________INPUT_LAST_LINE___________________________________________")
    logger.debug(list(q_ts_list))
    result_ts_list = q_ts_list.copy()
    for q in range(len(q_ts_list)):
            logger.debug("db_conn = " + str(db_conn))
            # q = q_list[i][j]
            query_str = "q={} AND \"ORG_ID\" = '{}' AND" \
                        " \"SERVICE_TYPE\" = '{}' AND \"TARGET_SYSTEM_SERVICE\" = '{}' AND {})".format(q_ts_list[q],
                                                                                                       bank,
                                                                                                       service,
                                                                                                       target_service,
                                                                                                       test_time)
            logger.debug("query_str = " + query_str)
            r = requests.get(db_conn, query_str)
            if r.status_code == 200 and r.text == "{\"results\":[{\"statement_id\":0}]}":
                result_ts_list[q] = '0'
            elif r.status_code == 200:
                logger.debug("HTTP CODE: ", r.status_code)
                logger.debug(r.text)
                try:
                    # json_data = r.json()
                    rs = json.loads(r.text)
                    series = rs["results"][0]['series'][0]
                    res_avg = int(series['values'][0][1])
                    logger.debug(res_avg)
                    # res_avg = int(rs['results'][0]['series'][0]['values'][0][1])  # округляем float до int
                    result_ts_list[q] = res_avg.__str__()
                except KeyError:
                    result_ts_list[q] = 'X'
            else:
                logger.debug("HTTP CODE: ", r.status_code)
                logger.debug(r.text)
                logger.debug("results_list ")
                logger.debug(result_ts_list)
                continue
                # raise Exception()
    logger.debug("__________________________________OUTPUT_LAST_LINE__________________________________________________")
    logger.debug(result_ts_list)
    return result_ts_list
