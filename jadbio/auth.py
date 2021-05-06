def json_headers(token):
    return {'Content-type':'application/json','Authorization': 'Bearer'+' '+token}

def headers(token, content_type):
    return {'Content-type':content_type,'Authorization': 'Bearer'+' '+token}