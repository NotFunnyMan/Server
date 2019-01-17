import requests

url = "https://fcm.googleapis.com/fcm/send"
data = ""

res = requests.post(url, json=data, verify=False)
print(res.reason)
pass
