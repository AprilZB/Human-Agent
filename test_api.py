import urllib.request
import urllib.error

try:
    req = urllib.request.Request('http://127.0.0.1:8100/api/v1/report/overtime')
    response = urllib.request.urlopen(req)
    print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
