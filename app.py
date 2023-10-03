from api import app
from asyncio import new_event_loop
import json, os

def dump(*dicts):
    for i in dicts:
        if isinstance(i, list):
            dump(*i)
        else:
            try: 
                i = i.to_dict()
            except Exception as e:
                pass
            print(json.dumps(i, indent=4))

if __name__ == '__main__':
    loop = new_event_loop()
    loop.run_until_complete(app.run(debug=True, host='0.0.0.0'))