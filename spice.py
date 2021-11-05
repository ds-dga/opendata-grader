from requests import Session, get
import json
import time
import spice_pusher

SPICE_UPTIME_URL = "https://ds.10z.dev/uptime"
sess = Session()

# https://en.wikipedia.org/wiki/Media_type
VALID_CONTENT_TYPES = [
    "application/json",
    "application/xml",
    "text/xml",
    "text/plain",
    "text/csv",
]

BAD_URLS = [
    "test.com",
    "example.com",
    "google.com",
]


def req_get(url):
    resp = get(url)
    resp_msg = None
    try:
        resp_msg = json.loads(resp.text)
    except:
        pass

    return resp.status_code, resp_msg


def get_uptime_record_for(url):
    resp = get(f"{SPICE_UPTIME_URL}?url={url}")
    resp_msg = None
    try:
        resp_msg = json.loads(resp.text)
    except:
        pass

    return resp.status_code, resp_msg


def create_uptime_record(name, url, group="opendata", frequency="", extras=None):
    body = {
        "name": name,
        "url": url,
        "group": group,
        "frequency": frequency,
    }
    if extras:
        body['extras'] = extras
    resp = sess.post(f"{SPICE_UPTIME_URL}?url={url}", json=body)
    resp_msg = None
    try:
        resp_msg = json.loads(resp.text)
    except:
        pass

    return resp.status_code, resp_msg


def is_good_content_type(target):
    """a bunch returns
    * text/xml; charset=utf-8
    * application/json; charset=utf-8
    """
    for ct in VALID_CONTENT_TYPES:
        if target.find(ct) > -1:
            return True
    return False


def is_real_api(url):
    # check if content-type is json or xml or text first
    # the rest is not classified as API
    is_valid = False
    for m in BAD_URLS:
        if url.find(m) != -1:
            return is_valid, "bad URL"
    resp_head = None
    try:
        resp_head = sess.head(url, timeout=10)
        headers = resp_head.headers
        content_type = headers["Content-Type"]
        is_valid = is_good_content_type(content_type)
        return is_valid, content_type
    except KeyError:
        return False, f"status_code = {resp_head.status_code}"
    except Exception as e:
        msg = f"{type(e)} - {e}"
        return False, msg


def uptime_record_test(url):

    s = time.time()
    try:
        resp = get(url, timeout=15)
        spice_pusher.push(resp)
        time.sleep(1)
    except:
        duration = time.time() - s
        spice_pusher.push_raw(url, 504, duration)  # 504 gateway timeout
        time.sleep(1)
        return
