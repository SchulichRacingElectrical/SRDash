import json
import http.client as httplib
import time


def create_json(data):
    json_str = json.dumps(data)
    return json_str


def readify_data(data):
    return create_json(data).encode("UTF-8")


def string_me(data):
    return json.loads(data.decode('utf-8'))


def replace_value_with_definition(current_dict, key_to_find, definition):
    for key in current_dict.keys():
        if key == key_to_find:
            current_dict[key] = definition
    return current_dict


def have_internet():
    start_time = time.time()
    conn = httplib.HTTPConnection("www.google.com", timeout=1)
    try:
        conn.request("HEAD", "/")
        conn.close()
        print(time.time()-start_time)
        return True
    except Exception as e:
        print("Internet not connected")
        print(time.time() - start_time)
        conn.close()
        return False
