import requests
import hashlib
import json
from requests.auth import HTTPBasicAuth

def send_bulk(host,elastic_index,list_doc,chunk_size,index,is_hash=False):

    for chunk in chunks(list_doc,chunk_size):
        f=open("bulk_data.json",'w+')
        for doc in chunk:
            doc_id = create_id(doc,index,is_hash)
            f.write('{"index":{"_id" : "'+ doc_id +'"}}\n')
            f.write(json.dumps(doc)+'\n')
        f.close()

        sending(host,elastic_index)
     
def create_id(doc,index,is_hash):
    the_id = ''
    for i in index:
        the_id+= str(doc[i])
    if is_hash:
        if len(doc['lemma']) != 0:
            the_id+= str(doc['lemma'])
        result = hashlib.md5(the_id.encode()) 
        the_id = result.hexdigest()
    return the_id

def sending(host,elastic_index):
    #sending
    host = host.rstrip('/')
    req = requests.post(f'{host}/{elastic_index}/_doc/_bulk',
                headers={"Content-Type":"application/x-ndjson"},
                auth = HTTPBasicAuth('elastic', 'E12qwaszx'),
                data=open('bulk_data.json', 'rb'))

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        