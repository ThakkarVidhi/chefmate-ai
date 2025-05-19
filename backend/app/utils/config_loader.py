import yaml
import os

def load_config(config_file: str = "config.yml") -> dict:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", config_file)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config