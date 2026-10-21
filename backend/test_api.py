import requests, json, sys
payload = {
    "text": "Artificial intelligence is very useful in education. It helps students learn faster.",
    "mode": "academic"
}
try:
    r = requests.post('http://127.0.0.1:8000/rewrite', json=payload, timeout=10)
    r.raise_for_status()
    print(r.json())
except Exception as e:
    print('Error:', e, file=sys.stderr)
