import yaml
import logging


_logger = logging.getLogger(__name__)


def write(fname, data):
    _logger.debug(f"Writing YAML file: {fname}")
    with open(fname, 'w+') as file:
        yaml.dump(data, file)


def read(fname):
    _logger.debug(f"Reading YAML file: {fname}")
    try:
        with open(fname) as file:
            return yaml.load(file, Loader=yaml.FullLoader)
    except ValueError:
        raise ValueError("File must be a YAML-formatted file")

