import json


def readjson():
    with open("userinfo.json", "r+") as f:
        j = json.loads(f.read())
        f.close()
        return j


def writejson(j):
    with open("userinfo.json", "wt") as f:
        f.write(j)
        f.close()


def search(arr, n, x):
    for i in range(0, n):
        if arr[i]["qq"] == x:
            return i
    return -1


def searchinfo(qq):
    arr = readjson()["data"]
    result = search(arr, len(arr), qq)
    if result == -1:
        return -1
    else:
        return arr[result]


def update(qq, email, token):
    i = searchinfo(qq)
    if i != -1:
        info = readjson()
        info["data"][i]["email"] = email
        info["data"][i]["token"] = token
        writejson(json.dumps(info))


def newuser(qq, email):
    data = {
        'qq': qq,
        'email': email,
        'token': ''
    }
    j = readjson()
    j["data"].append(data)
    writejson(json.dumps(j))


def binding():
    pass

# now = readjson()["lastregtime"]
# time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now))
