OVERWRITE_CONFIG = {
    'config': None,
    'db_adapter': None,
    'get_common_template_vals': lambda x: {"top_ad_target": "Resources", "side_ad_1_target": "Resources", "side_ad_2_target": "Resources"},
    'app': None
}


def get_config():
    return OVERWRITE_CONFIG
