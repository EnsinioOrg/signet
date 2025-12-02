import json

def convert_dict2json(data: dict, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(data, indent=4, sort_keys=True)
    return json.dumps(data)

def respond_json(data: dict, pretty: bool = False) -> None:
    print(convert_dict2json(data, pretty))