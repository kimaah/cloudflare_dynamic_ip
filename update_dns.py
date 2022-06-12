import requests
import time

CF_API_URL = "https://api.cloudflare.com/client/v4"
CF_HEADERS = {
    "Content-Type": "application/json",
    "X-Auth-Email": "EMAIL_ADDRESS@gmail.com",
    "X-Auth-Key": "CLOUDFLARE-API-KEY",
}

DOMAINCOM_ZONE_ID = "YOURDOMAIN.COM-ZONE-ID" # your domain's zone id (get it from the overview page of your domain on cloudflare)

CURRENT_IP = ""
SLEEP_TIME = 480 # time to wait between ip checks and updates (in seconds)

# get my ip address
def get_ip():
    try:
        r = requests.get("https://api.ipify.org")
        CURRENT_IP = r.text
        return r.text
    except:
        return 'x.x.x.x'

# get dns records
def get_dns(zone_id: str):
    try:
        r = requests.get(f"{CF_API_URL}/zones/{zone_id}/dns_records", headers=CF_HEADERS)
        res = r.json()
        return res["result"]
    except:
        return 'exception'

# update ip for dns record
def update_ip(zone_id: str, dns_data):
    dns_id = dns_data["id"]
    dns_type = dns_data["type"]
    dns_name = dns_data["name"]
    dns_proxied = dns_data["proxied"]
    ip = get_ip()
    if ip == 'x.x.x.x':
        return 'exception'
    if dns_type.lower() != 'a':
        return 'not_needed'
    d = {
        "type": dns_type,
        "name": dns_name,
        "proxied": dns_proxied,
        "content": ip,
        "ttl": 1
    }
    try:
        r = requests.put(f"{CF_API_URL}/zones/{zone_id}/dns_records/{dns_id}", headers=CF_HEADERS, json=d)
        return r.json()
    except:
        return 'exception'

# update domains every mins
while True:
    # DOMAIN.COM
    if CURRENT_IP != get_ip(): # check if ip changed
        dns_data = get_dns(zone_id=DOMAINCOM_ZONE_ID)
        if not dns_data == 'exception':
            # a loop that goes through all "A" type dns records
            for d_dat in dns_data:
                update_r = update_ip(zone_id=DOMAINCOM_ZONE_ID, dns_data=d_dat)
                try:
                    print(f"Updated the domain: {update_r['result']['name']}, updated successfully?: {update_r['success']}") # successfully updated the dns record
                except:
                    print(f"Failed to update a domain, response: {update_r}") # failed to update the dns record
    time.sleep(SLEEP_TIME)
