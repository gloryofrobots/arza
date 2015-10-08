__author__ = 'gloryofrobots'

def parse(txt):
    import requests
    import json
    r = requests.post("http://localhost:8084", data={'program': txt})
    ast = r.json()
    print json.dumps(ast, sort_keys=True,
                  indent=4, separators=(',', ': '))
