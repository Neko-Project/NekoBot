import aiohttp


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as r:
            if r.status == 200:
                return await r.read()


async def post(url, data) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=data) as r:
            if r.status == 200:
                return await r.json()
            else:
                return {'code': 0, 'msg': '网络爆炸惹qwq'}


def captcha():
    pass


def gravatar():
    pass


def siteConfig():
    pass


def rank():
    pass


async def dailycard(email, sel, id) -> dict:
    url = "http://116.85.72.173:3000/api/dailycard"
    data = {
        "email": email,
        "sel": sel,
        "packageId": id
    }
    return await post(url, data)


async def reg(email, password, nickName) -> dict:
    url = "http://116.85.72.173:3000/api/reg"
    data = {
        "email": email,
        "password": password,
        "nickName": nickName,
        "emailCode": "",
        "secretkey": "8248aea2e282c3ba0312155e43b8e43b"
    }
    return await post(url, data)


def find():
    pass


def searchcard():
    pass


def searchcardbytoken():
    pass


async def searchlog() -> dict:
    url = "http://116.85.72.173:3000/api/searchlog"
    data = {
        "page": 1
    }
    return await post(url, data)


def sendmail():
    pass


def login():
    pass


def userinfo():
    pass


def shop():
    pass


def logout():
    pass


async def news() -> dict:
    url = "http://116.85.72.173:3000/api/news"
    data = {
        "page": 1
    }
    return await post(url, data)


def marketsell():
    pass


def marketbuy():
    pass


def marketchart():
    pass


def battle():
    pass


def battlecard():
    pass


def decompose():
    pass


def decomposeitem():
    pass


def wantcard():
    pass


def searchwantcard():
    pass


def searchbattleinfo():
    pass


def searchcardlevel():
    pass


def searchuseritem():
    pass


def upgradecard():
    pass


def dailygetitem():
    pass


def dailygetitemmenu():
    pass


def cardlevelchange():
    pass


def searchbattlelogs():
    pass


def uploadcard():
    pass


def searchcardpackage():
    pass


def handbook():
    pass


def searchcrearchcard():
    pass


def searchguesscard():
    pass


def userguesscard():
    pass


def userpost():
    pass


def robotcheck():
    pass


def quest():
    pass


def uploadtx():
    pass


def admin_checkinstall():
    pass


def admin_install():
    pass


def admin_login():
    pass


def admin_setting():
    pass


def admin_givestar():
    pass


def admin_searchuser():
    pass


def admin_ban():
    pass


def admin_passwordchange():
    pass


def admin_logout():
    pass


def admin_secretkey():
    pass


def admin_searchlog():
    pass


def admin_news():
    pass


def admin_renamecardpackage():
    pass


def admin_creatcard():
    pass


def admin_searchcard():
    pass


def admin_editcard():
    pass


def admin_setrobotrate():
    pass
