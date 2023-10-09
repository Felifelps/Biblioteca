from api import app
from asyncio import new_event_loop
import json, os

port = os.getenv('PORT')

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
    app.run(port=port, host='0.0.0.0')