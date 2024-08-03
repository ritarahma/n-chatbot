from flask import current_app as app, request
import json
from flask import jsonify
import requests
from elasticsearch import Elasticsearch

def save_to_elassandra(url, index, data):
    # Save session information
    config = app.config['ELASTICSEARCH']
    hosts = app.elastic.transport.hosts
    path = 'http://'+hosts[0]['host']+':'+str(config['PORT'])+'/'+url+index
    return requests.put(path, json=data, verify=False).json()
    # return requests.put('http://117.54.250.99:19200/entity_aliasing/_doc/default',json={'username': 'default', 'alias': {'jokowidodo': ['jokaaaawidodo', 'jokowi']}},verify=False).json()
    

def get_data_list(prefix=None, keyword=None, start=None, end=None):
    if prefix is not None and keyword is not None:
        pattern = "{}:{}*".format(prefix, keyword)
    elif keyword is not None:
        pattern = "*{}*".format(keyword)
    elif start is not None and end is not None:
        pattern = "*{}*".format(start + '-' + end)
    else:
        return []

    results = []
    list_key = app.redis.keys(pattern)
    if list_key is not None:
        for key in list_key:
            results.append(key.decode('ASCII'))
    return results

def get_data_from_elassandra(url, data):
    config = app.config['ELASTICSEARCH']
    hosts = app.elastic.transport.hosts
    path = 'http://'+hosts[0]['host']+':'+str(config['PORT'])+'/'+url
    data = requests.get(path, json=data)
    
    return data
def elastic_scroller(es,index,doc_type,scroll_count=None,size=1000,body={}):
    data = es.search(
        index=index,
        doc_type=doc_type,
        body=body,
        size=size,
        scroll='10s',
        # clear_scroll = True,
    )
    # Get the scroll ID
    sid = data['_scroll_id']
    scroll_size = len(data['hits']['hits'])
    counter = 1
    all_hits=[]
    while scroll_size > 0:
    # while counter > 0:
        "Scrolling..."
        # Before scroll, process current batch of hits
        all_hits.extend(data['hits']['hits'])
        
        # Get next page
        # data = requests.get(path+'_search/scroll',json={'scroll':'10s','scroll_id':sid}).json()
        data = es.scroll(scroll_id=sid, scroll='10s')

        # Update the scroll ID
        sid = data['_scroll_id']

        # Get the number of results that returned in the last scroll
        scroll_size = len(data['hits']['hits'])

        # stop in n number all_hits scroll loop
        counter+=1
        if scroll_count:
            if counter > scroll_count:
                break
    return all_hits
 

def elassandra_scroller(index,scroll_count=None,size=1000,body={}):
    # Save session information
    config = app.config['ELASTICSEARCH']
    hosts = app.elastic.transport.hosts
    body['size']=size

    timeout = 1000
    doc_type = "_doc"

    # Init scroll by search
    path = 'http://'+hosts[0]['host']+':'+str(config['PORT'])+'/'
    init_path = path+index+'/_search?scroll=10s'
    data = requests.get(init_path, json=body).json()

    # Get the scroll ID
    sid = data['_scroll_id']
    scroll_size = len(data['hits']['hits'])
    counter = 1
    all_hits=[]
    while scroll_size > 0:
    # while counter > 0:
        "Scrolling..."
        # Before scroll, process current batch of hits
        all_hits.extend(data['hits']['hits'])
        
        # Get next page
        data = requests.get(path+'_search/scroll',json={'scroll':'10s','scroll_id':sid}).json()

        # Update the scroll ID
        sid = data['_scroll_id']

        # Get the number of results that returned in the last scroll
        scroll_size = len(data['hits']['hits'])

        # stop in n number all_hits scroll loop
        counter+=1
        if scroll_count:
            if counter > scroll_count:
                break
    return all_hits

def clear_data(prefix=None, keyword=None):
    if prefix is not None and keyword is not None:
        prev_session = get_data_list(prefix=prefix, keyword=keyword)

    if len(prev_session) > 0:
        prev_session = list(key for key in prev_session)
        app.redis.delete(*prev_session)