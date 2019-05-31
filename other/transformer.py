import json

# columns = ['time'] + list(next(iter(data[0]['input_data']['rwis_data'].values())).keys())

with open("51527.json", encoding='utf-8') as json_file:
    data = json.load(json_file)

columns = ['time'] + list(next(iter(data[0]['input_data']['rwis_data'].values())).keys())

result_json = {}

for item in data:
    batch = item['input_data']['rwis_data']
    for key, value in batch.items():
        row = list(batch[key].values())
        result_json[key] = value

with open("51527a.json", "w") as outfile:
    json.dump(result_json, outfile)