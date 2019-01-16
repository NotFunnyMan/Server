import requests

url = "https://fcm.googleapis.com/fcm/send"
header = {'Content-Type': 'application/json',
          'Authorization': 'key=AAAAxaZ1Qa0:APA91bFrSiIuCHsDmSM4vBcz_9tURmGHd2keYHoovCreG5jftpogfeEvTSu8Qk7MymFnmS71Dou2ANfd2L7uXGnWo16gdypXh4rx30xUMiwlSPo3DTEtrDXefZXai8Pk0usSgBcdQfbX9V83yyOqE1AxlmTxjtNljQ'}

my_phone = "egSjTOCe3Y4:APA91bGI5YKAwBXdAxa44jMQndc69Ya_F5L3FYK4RINwmrVsIRPGuxD3KlAdx4A9i3MlWp5sAVStkK5Xyx_XBPAi_644aGPVg0MkE02UPXaUy2mBDCCf-6ihQngL4ue3Oi40ohvDqTKNq-QCLzGboUfwcYl8UNlmRg"
moms_phone = "cVlwEWGhcb0:APA91bHtkiJ9l7gSGVd-B2Vch3s4yQ_x9c9NUeJHhf7yQqJY1R5v0xdEqHYqfR8zuM7obwYJIjByLQHNQZR-hE2xceuzKnv3vC9bovvne3hutTUTIRHCX3FvVXGX-M-z7hsogd4Dy7qsFJjBYlwpMH_nkfRcKxonmg"
emulator = "fQcEmWa2IYA:APA91bF4LwLgza1JLGEuj8Z8KdBfYYD4N9DoOmMF-10Uuwkbq58X5G5PFe1MkvobsgcXywbfiPSka752JQ47gAauKM9rHCnzlTHqww8kQm--vuy62-PeZL_lRpD8PFHbZerdj3wOR9M8ISvSMSbMRfJgcLOpNKCgyw"


def Send(updates, resource):
    i = 0
    for update in updates:
        data = {
                "data":
                    {
                        "body": update.title,
                        "title": "Вышла новая серия сериала на " + resource,
                        "icon": "http://" + update.description,
                        "resource": resource,
                        "sound": "default",
                        "priority": "high",
                        "id": i
                    },
                "to": my_phone
                }
        res = requests.post(url, headers=header, json=data, verify=False)
        print(res)
        i += 1
