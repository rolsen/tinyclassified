OVERWRITE_CONFIG = {
    'config': None,
    'db_adapter': None,
    'get_common_template_vals': lambda x: {},
    'app': None
}


def get_config():
    return OVERWRITE_CONFIG
