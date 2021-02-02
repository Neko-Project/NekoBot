import random

import requests


def moli(word):
    api_key = "57d8d9ecdc643f69906c541ec64d3fb9"
    api_secret = "Miaow"
    url = "http://i.itpk.cn/api.php?limit=3&api_key=%s&api_secret=%s&question=%s" % (
        api_key, api_secret, word)
    r = requests.get(url)
    r.encoding = "utf-8"
    if r.status_code == 200:
        return r.text
    else:
        return random.choice(["喵喵酱现在不想和你说话", "喵喵酱还在睡觉呢"])


if __name__ == "__main__":
    print(moli("444"))
