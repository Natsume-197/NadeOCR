import configparser

path_config_ini = './settings/config.ini'

def read_config_ini():
    config_reader = configparser.ConfigParser()
    config_reader.read(path_config_ini)
    return config_reader

def edit_config_ini(section, option, value):
    config_reader = configparser.ConfigParser()
    config_reader.read(path_config_ini)
     
    with open(path_config_ini, 'w') as configfile:
        config_reader.set(section, option, value)
        config_reader.write(configfile)

def to_boolean(value):
    if str(value).lower() in ("true", "1"): return True
    if str(value).lower() in ("false", "0", "", "none", "[]"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))

