import configparser
import logging
import os


module_logger = logging.getLogger("Perf_reporter.config")


def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "db_host", "localhost")
    config.set("Settings", "db_port", "8086")
    config.set("Settings", "db_name", "monitoringData")
    config.set("Settings", "db_start", "'2019-07-31 00:06:54'")
    config.set("Settings", "db_end", "'2019-07-31 03:09:33'")
    config.set("Settings", "db_info",
               "You are using database host: %(db_host)s "
               "at port: %(db_port)s "
               "with database: %(db_name)s "
               "and time: %(db_start)s - %(db_end)s")
    config.set("Settings", "confluence_user", "USR")
    config.set("Settings", "confluence_password", "PASSWORD")
    config.set("Settings", "confluence_url", "https://10.119.16.119/confluence")
    config.set("Settings", "confluence_space", "EPAM")
    config.set("Settings", "confluence_page_id", "id")
    config.set("Settings", "grafana_url", "http://localhost:8090")
    config.set("Settings", "garafana_dashboard_uri", "/render/d-solo/kD8ewDnmz/prf06")
    config.set("Settings", "grafana_org_id", "1")
    config.set("Settings", "grafana_panel_id_list", ['75','76','73','74','40','72','69','68','67','44','43','46','12','13','53','54','6','5'])
    config.set("Settings", "grafana_panel_width", {'75': "680", '76': "680", '73': "680", '74': "680", '40': "680", '72': "680", '69': "680", '68': "680", '67': "680", '44': "680", '43': "680", '46': "680", '12': "680", '13': "680", '53': "680", '54': "680", '6': "680", '5': "680"})
    config.set("Settings", "grafana_panel_height", {'75': "250", '76': "250", '73': "250", '74': "250", '40': "250", '72': "250", '69': "250", '68': "250", '67': "250", '44': "250", '43': "250", '46': "250", '12': "250", '13': "250", '53': "250", '54': "250", '6': "250", '5': "250"})

    with open(path, "w") as config_file:
        config.write(config_file)
    logger = logging.getLogger("Perf_reporter.config.create_config")
    logger.info('Config created')


def get_config(path):
    """
    Returns the config object
    """
    if not os.path.exists(path):
        create_config(path)

    config = configparser.ConfigParser()
    config.read(path)
    return config


def get_setting(path, section, setting, msg=0):
    """
    Print out a setting
    """
    config = get_config(path)
    value = config.get(section, setting)
    if msg:
        msg = "{section} {setting} is {value}".format(
            section=section, setting=setting, value=value
        )
    logger = logging.getLogger("Perf_reporter.config.get_setting")
    logger.info('Set setting: ' + setting)
    return value


def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "w") as config_file:
        config.write(config_file)
    logger = logging.getLogger("Perf_reporter.config.update_setting")
    logger.info('Updated setting: ' + setting)


def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "w") as config_file:
        config.write(config_file)
    logger = logging.getLogger("Perf_reporter.config.delete_setting")
    logger.info('Deleted setting: ' + setting)