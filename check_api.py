import urllib.request, json, os

try:
    h = urllib.request.urlopen("http://localhost:8000/health")
    print("Health:", json.loads(h.read()))
except Exception as e:
    print("Health Error:", str(e))

try:
    iden = urllib.request.urlopen("http://localhost:8000/identities")
    print("DB Identities:", json.loads(iden.read()))
except Exception as e:
    print("DB Identities Error:", str(e))

print("DB File Exists:", os.path.exists("insa_identity.db"))
