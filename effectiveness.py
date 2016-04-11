# -*- coding: utf-8 -*-

import datetime, collections, json

from matplotlib import pyplot

with open('results.json') as f:
    all_results_json = f.read()
all_results = json.loads(all_results_json)

all_names = set()
for results in all_results:
    for person_dict in results['scores']:
        all_names.add(person_dict['name'])

name_to_scores = collections.defaultdict(list)
dt = datetime.datetime(2016, 2, 1)
dts = []
for results in all_results:
    dts.append(dt)
    seen_names = set()
    for person_dict in results['scores']:
        name, score = person_dict['name'], person_dict['score']
        seen_names.add(name)
        name_to_scores[name].append(score)
    for missing_name in all_names - seen_names:
        name_to_scores[missing_name].append(0)
    if dt.day == 1:
        dt = dt.replace(day=15)
    else:
        dt = dt.replace(month=dt.month + 1)
        dt = dt.replace(day=1)

for name, scores in name_to_scores.iteritems():
    pyplot.plot(dts, scores)
pyplot.xticks(dts)
pyplot.savefig('historical_scores.png')
pyplot.show()
