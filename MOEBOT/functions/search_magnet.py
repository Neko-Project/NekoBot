import aiohttp
from bs4 import BeautifulSoup
from urllib import parse
import re

from graia.application.message.elements.internal import Plain
from graia.application.message.elements.internal import Image
from graia.application.message.chain import MessageChain

from MOEBOT.basics.tools import text2piiic
from MOEBOT.data_manage.get_data.get_setting import get_setting
from MOEBOT.functions.get_proxy import get_proxy


async def search_magnet_old(keyword: str, group_id: int) -> list:
    url = f"https://btsow.com/search/{keyword}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        "referer": f"https://btsow.com/search/{keyword}"
    }
    print(url)

    proxy = await get_proxy()
    proxies = {"http": f"http://{proxy['proxy']}"} if proxy.get("proxy") else None
    print("proxy:", proxies)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, proxy=proxies["http"]) as resp:
                html = await resp.text()
    except (aiohttp.client_exceptions.ClientHttpProxyError,
            aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientOSError,
            TypeError):
        return [
            "quoteSource",
            MessageChain.create([
                Plain(text="Proxy Error!")
            ])
        ]

    # print("html:", html)
    if not html:
        return [
            "None",
            MessageChain.create([
                Plain("IP可能被屏蔽！")
            ])
        ]
    records = list()
    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("div", {"class": "data-list"}).find_all("div", {"class": "row"})

    count = 0

    for div in data:
        count += 1
        if count > 5:
            break
        record = dict()
        # print(div)
        try:
            record["link"] = div.find("a", href=True)["href"]

            async with aiohttp.ClientSession() as session:
                async with session.get(url=record["link"]) as resp:
                    magnet_html = await resp.text()
            # print(magnet_html)
            record["magnet"] = re.findall(
                r'<textarea id="magnetLink" name="magnetLink" class="magnet-link hidden-xs" readonly>(.*?)</textarea>',
                magnet_html, re.S)[0]
            record["title"] = div.find("a").find("div", {"class": "file"}).get_text()
            record["size"] = div.find("div", {"class": "size"}).get_text()
            record["date"] = div.find("div", {"class": "date"}).get_text()
            records.append(record)
        except TypeError:
            pass

    text = "--------------------\n搜索到结果：\n"
    for data in records:
        text += f"标题：{data['title']}\n"
        text += f"大小：{data['size']}\n"
        text += f"日期：{data['date']}\n"
        text += f"磁力：{data['magnet']}\n"
        text += "--------------------\n"

    long_text_setting = await get_setting(group_id, "longTextType")
    if long_text_setting == "img":
        img = text2piiic(string=text, poster="", length=max(len(x) for x in text.split("\n")))
        img.save("./statics/temp/tempMagnet.png")
        return [
            "quoteSource",
            MessageChain.create([
                Image.fromLocalFile("./statics/temp/tempMagnet.png")
            ])
        ]
    elif long_text_setting == "text":
        return [
            "quoteSource",
            MessageChain.create([
                Plain(text=text)
            ])
        ]
    else:
        return [
            "None",
            MessageChain.create([
                Plain(text="数据库 longTextType 项出错！请检查！")
            ])
        ]


async def search_magnet(keyword: str, group_id: int, audio: bool = False, video: bool = False, app: bool = False,
                  games: bool = False, porn: bool = False):
    args = "100,200,300,400,500"
    if not audio:
        args = args.replace("100,", "")
    if not video:
        args = args.replace("200,", "")
    if not app:
        args = args.replace("300,", "")
    if not games:
        args = args.replace("400,", "")
    if not porn:
        if len(args) == 3:
            args = "0"
        else:
            args = args.replace(",500", "")

    url = f"https://tpb.party/search/{keyword}/1/99/{args}"
    print(url)
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            html = await resp.text()
    soup = BeautifulSoup(html, "html.parser")
    data = soup.find("table").find_all("tr")
    divs = []
    for i in data:
        div = i.find("div", {"class": "detName"})
        if div:
            if div and div.find("a").get_text() not in divs:
                divs.append(div)
    records = []
    count = 0
    for i in divs:
        count += 1
        if count > 5:
            break
        record = {"title": i.get_text().strip()}
        print(record["title"])
        record["href"] = i.find("a", href=True)["href"]

        async with aiohttp.ClientSession() as session:
            async with session.get(url=record["href"], headers=headers) as resp:
                html_torrent = await resp.text()

        soup_torrent = BeautifulSoup(html_torrent, "html.parser")
        record["magnet"] = soup_torrent.find("div", {"class": "download"}).find_all("a", href=True)[0]["href"]
        records.append(record)

    text = "--------------------\n搜索到结果：\n"
    for data in records:
        # print(parse.unquote(''.join(data['magnet'].split('&')[:2])))
        # print(data['magnet'])
        text += f"标题：{data['title']}\n"
        text += f"磁力：{parse.unquote('&'.join(data['magnet'].split('&')[:2]))}\n"
        text += "--------------------\n"

    long_text_setting = await get_setting(group_id, "longTextType")
    if long_text_setting == "img":
        img = text2piiic(string=text, poster="", length=max(len(x) for x in text.split("\n")))
        img.save("./statics/temp/tempMagnet.png")
        return [
            "quoteSource",
            MessageChain.create([
                Plain(text="为防止tx吞超长文本及封禁此账号，已将链接转为图片格式，请自行使用OCR（有毅力的也可以手打）获取链接！\n"),
                Image.fromLocalFile("./statics/temp/tempMagnet.png")
            ])
        ]
    elif long_text_setting == "text":
        return [
            "quoteSource",
            MessageChain.create([
                Plain(text=text)
            ])
        ]
    else:
        return [
            "None",
            MessageChain.create([
                Plain(text="数据库 longTextType 项出错！请检查！")
            ])
        ]
