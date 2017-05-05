from collections import defaultdict
import random


HofmannCIKM11 = {
    'perfect': {
        'click': [0.00, 0.20, 0.40, 0.80, 1.00],
        'stop':  [0.00, 0.00, 0.00, 0.00, 0.00],
    },
    'realistic': {
        'click': [0.05, 0.10, 0.20, 0.40, 0.80],
        'stop':  [0.00, 0.20, 0.40, 0.60, 0.80],
    },
}
SchuthCIKM14 = {
    'perfect':
        {'click': [0.0,  0.5,  1.0],  'stop': [0.0,  0.0,  0.0]},
    'navigational':
        {'click': [0.05, 0.5,  0.95], 'stop': [0.2,  0.5,  0.9]},
    'informational':
        {'click': [0.4,  0.7,  0.9],  'stop': [0.1,  0.3,  0.5]},
    'random':
        {'click': [0.5,  0.5,  0.5],  'stop': [0.0,  0.0,  0.0]},
}
SchuthSIGIR15 = {
    'perfect':       {'click': [0.0,  1.0],  'stop': [0.0,  0.0]},
    'navigational':  {'click': [0.05, 0.95], 'stop': [0.2,  0.9]},
    'informational': {'click': [0.4,  0.9],  'stop': [0.1,  0.5]},
    'random':        {'click': [0.5,  0.5],  'stop': [0.0,  0.0]},
}
SchuthWSDM16 = {
    'perfect':
        SchuthCIKM14['perfect'],
    'navigational':
        SchuthCIKM14['navigational'],
    'informational':
        SchuthCIKM14['informational'],
    'almost random':
        {'click': [0.4,  0.5,  0.6],  'stop': [0.5,  0.5,  0.5]},
}


def click(relevance,
          run,
          intent_id='0',
          model=SchuthSIGIR15['perfect']):
    '''returns a dict where query_id -> a list of clicked indexes.'''
    result = defaultdict(list)
    for query_id, ranking in run.items():
        for index, document_id in enumerate(ranking):
            r = relevance[query_id][intent_id][document_id]
            if random.random() < model['click'][r]:  # Clicked
                result[query_id].append(index)
                if random.random() < model['stop'][r]:  # Stopped
                    break
    return result
