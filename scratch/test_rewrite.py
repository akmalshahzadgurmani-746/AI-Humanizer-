import requests, json
url='http://127.0.0.1:8000/rewrite'
payload={'text':'The quick brown fox jumps over the lazy dog.','mode':'academic'}
resp=requests.post(url,json=payload)
print('Status:',resp.status_code)
print('Response:',resp.text)
