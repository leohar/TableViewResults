import configparser
import os

def create_config(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "db_host", "127.0.0.1")
    config.set("Settings", "db_port", "8086")
    config.set("Settings", "db_name", "mydb")
    config.set("Settings", "db_info",
               "You are using host %(db_host)s at port:%(db_port)s with database: %(db_name)s")

    with open(path, "w") as config_file:
        config.write(config_file)


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

    print(msg)
    return value


def update_setting(path, section, setting, value):
    """
    Update a setting
    """
    config = get_config(path)
    config.set(section, setting, value)
    with open(path, "w") as config_file:
        config.write(config_file)


def delete_setting(path, section, setting):
    """
    Delete a setting
    """
    config = get_config(path)
    config.remove_option(section, setting)
    with open(path, "w") as config_file:
        config.write(config_file)