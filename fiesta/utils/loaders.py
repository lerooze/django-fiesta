import yaml

from string import Template


from .datastructures import AttrDict


def load_yaml(path):
    with open(path, 'r') as stream:
        data = yaml.load(stream, Loader=yaml.FullLoader)
    return AttrDict.recursive(data)

def load_error_descriptions(path):
    error_descriptions = load_yaml(path)
    for key, value in error_descriptions.items():
        if value.get('template'):
            for lang, template in value.text:
                value[lang]= Template(template)
    return error_descriptions

