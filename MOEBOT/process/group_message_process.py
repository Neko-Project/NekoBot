import re
import os
import pkuseg
import asyncio

from graia.application.event.messages import *
from graia.application import GraiaMiraiApplication
from graia.application.message.elements.internal import At

from MOEBOT.images.get_image import get_pic
from MOEBOT.basics.get_config import get_config
from MOEBOT.crawer.weibo.weibo_crawer import get_weibo_hot
from MOEBOT.crawer.zhihu.zhihu_crawer import get_zhihu_hot
from MOEBOT.crawer.github.github_crawer import get_github_hot
from MOEBOT.crawer.bilibili.bangumi_crawer import formatted_output_bangumi
from MOEBOT.crawer.leetcode.leetcode_user_info_crawer import get_leetcode_statics
from MOEBOT.crawer.steam.steam_game_info_crawer import get_steam_game_search
from MOEBOT.data_manage.get_data.get_setting import get_setting
from MOEBOT.data_manage.update_data.set_get_image_ready import set_get_img_ready
from MOEBOT.data_manage.get_data.get_image_ready import get_image_ready
from MOEBOT.crawer.saucenao.search_image import search_image
from MOEBOT.images.image_yellow_judge import image_yellow_judge
from MOEBOT.crawer.tracemoe.search_bangumi import search_bangumi
from MOEBOT.data_manage.update_data.update_dragon import update_dragon_data
from MOEBOT.images.get_wallpaper_time import get_wallpaper_time
from MOEBOT.images.get_wallpaper_time import show_clock_wallpaper
from MOEBOT.functions.get_translate import get_translate
from MOEBOT.data_manage.update_data.update_user_called_data import update_user_called_data
from MOEBOT.functions.order_music import get_song_ordered
from MOEBOT.functions.get_history_today import get_history_today
from MOEBOT.process.setting_process import setting_process
from MOEBOT.process.reply_process import reply_process
from MOEBOT.crawer.bangumi.get_bangumi_info import get_bangumi_info
from MOEBOT.data_manage.get_data.get_admin import get_admin
from MOEBOT.data_manage.get_data.get_blacklist import get_blacklist
from MOEBOT.data_manage.get_data.get_rank import get_rank
from MOEBOT.basics.write_log import write_log
from MOEBOT.functions.get_joke import *
from MOEBOT.functions.get_group_quotes import get_group_quotes
from MOEBOT.functions.get_jlu_csw_notice import get_jlu_csw_notice
from MOEBOT.basics.get_response_set import get_response_set
from MOEBOT.images.get_setu_keyword import get_setu_keyword
from MOEBOT.functions.petpet import petpet
from MOEBOT.functions.pornhub_style_image import make_ph_style_logo
from MOEBOT.functions.get_abbreviation_explain import get_abbreviation_explain
from MOEBOT.functions.search_magnet import search_magnet
from MOEBOT.data_manage.update_data.write_chat_record import write_chat_record
from MOEBOT.functions.get_review import *
from MOEBOT.basics.frequency_limit_module import GlobalFrequencyLimitDict
from MOEBOT.data_manage.update_data.save_birthday import save_birthday
from MOEBOT.functions.register import register
from MOEBOT.functions.check996 import check996
from MOEBOT.crawer.Zlib.search_pdf import search_pdf
from MOEBOT.functions.make_qrcode import make_qrcode
# from MOEBOT.functions.object_predict import object_predict_vgg16
from MOEBOT.data_manage.update_data.update_total_calls import update_total_calls
from MOEBOT.data_manage.update_data.update_total_calls import update_total_calls_once
from MOEBOT.data_manage.get_data.get_total_calls import get_total_calls
from MOEBOT.bot_status.get_gallery_status import get_gallery_status
from MOEBOT.crawer.douban.get_book_recommand_by_tag import get_book_recommand_by_tag
from MOEBOT.basics.keyword_reply import keyword_reply
from MOEBOT.crawer.runoob.network_compile import network_compile
from MOEBOT.bot_status.get_user_info import get_user_info
from MOEBOT.bot_status.get_system_status import get_system_status

# 关键词字典
response_set = get_response_set()

seg = pkuseg.pkuseg()


async def limit_exceeded_judge(group_id: int, weight: int):
    frequency_limit_instance = GlobalFrequencyLimitDict()
    if frequency_limit_instance.get(group_id) + weight >= 10:
        return [
            "quoteSource",
            MessageChain.create([
                Plain(text="Frequency limit exceeded every 10 seconds!")
            ])
        ]
    else:
        frequency_limit_instance.update(group_id, weight)
        return None


async def group_message_process(
        message: MessageChain,
        message_info: GroupMessage,
        app: GraiaMiraiApplication,
        frequency_limit_dict: dict
) -> list:
    """
    Process the received message and return the corresponding message

    Args:
        message: Received message(MessageChain)
        message_info: Received message(GroupMessage)
        app: APP
        frequency_limit_dict: Frequency limit dict

    Examples:
        message_list = await message_process(message, message_info)

    Return:
        [
            str: Auxiliary treatment to be done(Such as add statement),
            MessageChain: Message to be send(MessageChain)
        ]
    """
    message_text = message.asDisplay()
    message_serialization = message.asSerializationString()
    sender = message_info.sender.id
    group_id = message_info.sender.group.id
    # 黑名单检测
    if sender in await get_blacklist():
        print("Blacklist!No reply!")
        return ["None"]

    await write_chat_record(seg, group_id, sender, message_text)

    # print("message_serialization:", message_serialization)

    if message.has(At) and message.get(At)[0].target == await get_config("BotQQ"):
        await update_user_called_data(group_id, sender, "at", 1)

    if message.has(At) and message.get(At)[0].target == await get_config("BotQQ") and re.search(".* setting.*",
                                                                                                message_text):
        try:
            _, config, new_value = message_text.split(".")
            return await setting_process(group_id, sender, config, new_value)
        except ValueError:
            return [
                "None",
                MessageChain.create([
                    Plain(text="Command Error!")
                ])
            ]

    if message_text.startswith("/status"):
        if message_text.startswith("/status "):
            base_name = message_text[8:]
            if base_name:
                return await get_gallery_status(base_name)
            else:
                return [
                    "quoteSource",
                    MessageChain.create([
                        Plain(text="请给出base_name!")
                    ])
                ]
        elif message_text == "/status":
            return await get_system_status()
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="请给出base_name!")
                ])
            ]

    if message_text.lower() == "/myinfo":
        return await get_user_info(group_id, sender, message_info.sender.name, len(await app.memberList(group_id)))

    """
    图片功能：
        setu
        real
        bizhi
        time
        search
        yellow predict
        lsp rank
    """
    if message_text in response_set["setu"]:

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "setu"):
            if sender == 80000000:
                return [
                    "None",
                    MessageChain.create([
                        Plain(text="要涩图就光明正大！匿名算什么好汉！")
                    ])
                ]
            await update_dragon_data(group_id, sender, "normal")
            await update_user_called_data(group_id, sender, "setu", 1)
            await update_total_calls_once("response")
            await update_total_calls_once("setu")
            if await get_setting(group_id, "r18"):
                return await get_pic("setu18", group_id, sender)
            else:
                return await get_pic("setu", group_id, sender)
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")
                ])
            ]

    elif message_text.startswith("来点") and re.search("来点.*[色涩]图", message_text):

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 3)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "setu"):
            if sender == 80000000:
                return [
                    "None",
                    MessageChain.create([
                        Plain(text="要涩图就光明正大！匿名算什么好汉！")
                    ])
                ]
            keyword = re.findall("来点(.*?)[涩色]图", message_text, re.S)[0]
            print(keyword)
            if keyword in ["r18", "R18", "r-18", "R-18"]:
                return [
                    "quoteSource",
                    MessageChain.create([
                        Plain(text="此功能暂时还不支持搜索R18涩图呐~忍忍吧LSP！")
                    ])
                ]
            # await app.sendGroupMessage(

            await update_dragon_data(group_id, sender, "normal")
            await update_user_called_data(group_id, sender, "setu", 1)
            await update_total_calls_once("response")
            await update_total_calls_once("setu")
            return await get_setu_keyword(keyword=keyword)
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")
                ])
            ]

    elif message_text in response_set["real"]:

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "real"):
            if sender == 80000000:
                return [
                    "None",
                    MessageChain.create([
                        Plain(text="要涩图就光明正大！匿名算什么好汉！")
                    ])
                ]
            await update_dragon_data(group_id, sender, "normal")
            await update_user_called_data(group_id, sender, "real", 1)
            await update_total_calls_once("response")
            await update_total_calls_once("real")
            return await get_pic("real", group_id, sender)
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")
                ])
            ]

    elif message_text in response_set["realHighq"]:

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "real"):
            if sender == 80000000:
                return [
                    "None",
                    MessageChain.create([
                        Plain(text="要涩图就光明正大！匿名算什么好汉！")
                    ])
                ]
            await update_dragon_data(group_id, sender, "normal")
            await update_user_called_data(group_id, sender, "real", 1)
            await update_total_calls_once("response")
            await update_total_calls_once("real")
            return await get_pic("realHighq", group_id, sender)
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="我们是正规群呐，不搞那一套哦，想看去辣种群看哟~")
                ])
            ]

    elif message_text in response_set["bizhi"]:

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "bizhi"):
            if sender == 80000000:
                return [
                    "None",
                    MessageChain.create([
                        Plain(text="要涩图就光明正大！匿名算什么好汉！")
                    ])
                ]
            await update_user_called_data(group_id, sender, "bizhi", 1)
            await update_total_calls_once("response")
            await update_total_calls_once("bizhi")
            return await get_pic("bizhi", group_id, sender)
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="壁纸功能关闭了呐~想要打开的话就联系管理员吧~")
                ])
            ]

    elif message_text.startswith("setu*") or message_text.startswith("real*") or message_text.startswith("bizhi*"):
        if message_text.startswith("bizhi*"):
            command = "bizhi"
            num = message_text[6:]
        else:
            command = message_text[:4]
            num = message_text[5:]
        if num.isdigit():
            num = int(num)
            if sender not in await get_admin(group_id):
                if 0 <= num <= 5:
                    return [
                        "None",
                        MessageChain.create([
                            Plain(text="只有主人和管理员可以使用%s*num命令哦~你没有权限的呐~" % command)
                        ])
                    ]
                elif num < 0:
                    return [
                        "None",
                        MessageChain.create([
                            Plain(text="%d？你有问题？不如给爷吐出%d张来" % (num, -num))
                        ])
                    ]
                else:
                    return [
                        "None",
                        MessageChain.create([
                            Plain(text="不是管理员你要你🐎呢？老色批！还要那么多？给你🐎一拳，给爷爬！")
                        ])
                    ]
            if num < 0:
                return [
                    "None",
                    MessageChain.create([
                        Plain(text="%d？你有问题？不如给爷吐出%d张来" % (num, -num))
                    ])
                ]
            elif num > 5:
                if sender == await get_config("HostQQ"):
                    return ["%s*" % command, num]
                else:
                    return [
                        "None",
                        MessageChain.create([
                            Plain(text="管理最多也只能要5张呐~我可不会被轻易玩儿坏呢！！！！")
                        ])
                    ]
            else:
                if sender != await get_config("HostQQ"):
                    await update_user_called_data(group_id, sender, command, num)
                return ["%s*" % command, int(num)]
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="必须为数字！")
                ])
            ]

    elif message_text == "几点了":
        await update_total_calls_once("response")
        return await get_wallpaper_time(group_id, sender)

    elif message_text.startswith("选择表盘"):
        await update_total_calls_once("response")
        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        if message_text == "选择表盘":
            return await show_clock_wallpaper(sender)

    elif message_text == "搜图":
        await update_total_calls_once("response")
        await update_total_calls_once("search")
        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "search"):
            await set_get_img_ready(group_id, sender, True, "searchReady")
            await app.sendGroupMessage(
                group_id,
                MessageChain.create([
                    At(sender),
                    Plain(text="请在30秒内发送要搜索的图片呐~(仅支持pixiv图片搜索呐！)")
                ])
            )
            await asyncio.sleep(30)
            await set_get_img_ready(group_id, sender, False, "searchReady")
            return ["None"]
        else:
            return [
                "None",
                MessageChain.create([
                    At(sender),
                    Plain(text="搜图功能关闭了呐~想要打开就联系管理员吧~")
                ])
            ]
    elif message.has(Image) and await get_setting(group_id, "search") and await get_image_ready(group_id, sender,
                                                                                                "searchReady"):
        image = message.get(Image)[0]
        await update_user_called_data(group_id, sender, "search", 1)
        await update_total_calls_once("response")
        await update_total_calls_once("search")
        return await search_image(group_id, sender, image)

    elif message_text == "这张图涩吗":

        await update_total_calls_once("response")
        await update_total_calls_once("yellow")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "yellowPredict"):
            await set_get_img_ready(group_id, sender, True, "yellowPredictReady")
            await app.sendGroupMessage(
                group_id,
                MessageChain.create([
                    At(sender),
                    Plain(text="请在30秒内发送要预测的图片呐~")
                ])
            )
            await asyncio.sleep(30)
            await set_get_img_ready(group_id, sender, False, "yellowPredictReady")
            return ["None"]
        else:
            return [
                "None",
                MessageChain.create([
                    At(target=sender),
                    Plain(text="图片涩度评价功能关闭了呐~想要打开就联系机器人管理员吧~")
                ])
            ]
    elif message.has(Image) and await get_setting(group_id, "yellowPredict") and await get_image_ready(group_id, sender,
                                                                                                       "yellowPredictReady"):
        image = message.get(Image)[0]
        await update_user_called_data(group_id, sender, "yellowPredict", 1)
        await update_total_calls_once("response")
        await update_total_calls_once("yellow")
        return await image_yellow_judge(group_id, sender, image, "yellowPredict")

    # elif message_text == "这张图里是什么":
    #
    #     if await get_setting(group_id, "countLimit"):
    #         frequency_limit_res = await limit_exceeded_judge(group_id, 6)
    #         if frequency_limit_res:
    #             return frequency_limit_res
    #
    #     if await get_setting(group_id, "imgPredict"):
    #         await set_get_img_ready(group_id, sender, True, "predictReady")
    #         return [
    #             "None",
    #             MessageChain.create([
    #                 At(sender),
    #                 Plain(text="请发送要搜索的图片呐~(仅支持现实图片搜索呐！)")
    #             ])
    #         ]
    #     else:
    #         return [
    #             "None",
    #             MessageChain.create([
    #                 At(sender),
    #                 Plain(text="现实图片预测功能关闭了呐~想要打开就联系管理员吧~")
    #             ])
    #         ]
    # elif message.has(Image) and await get_setting(group_id, "imgPredict") and await get_image_ready(group_id, sender,
    #                                                                                             "predictReady"):
    #     # print("status:", await get_image_ready(group_id, sender, "searchReady"))
    #     image = message.get(Image)[0]
    #     await update_user_called_data(group_id, sender, "imgPredict", 1)
    #     return await object_predict_vgg16(group_id, sender, image)

    elif message_text == "搜番":

        await update_total_calls_once("response")
        await update_total_calls_once("search")
        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        if await get_setting(group_id, "searchBangumi"):
            await set_get_img_ready(group_id, sender, True, "searchBangumiReady")
            await app.sendGroupMessage(
                group_id,
                MessageChain.create([
                    At(sender),
                    Plain(text="请在30秒内发送要预测的图片呐~")
                ])
            )
            await asyncio.sleep(30)
            await set_get_img_ready(group_id, sender, False, "searchBangumiReady")
            return ["None"]
        else:
            return [
                "None",
                MessageChain.create([
                    At(sender),
                    Plain(text="搜番功能关闭了呐~想要打开就联系管理员吧~")
                ])
            ]
    elif message.has(Image) and await get_setting(group_id, "searchBangumi") and await get_image_ready(group_id, sender,
                                                                                                       "searchBangumiReady"):

        await update_total_calls_once("response")
        await update_total_calls_once("search")
        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        # print("status:", await get_image_ready(group_id, sender, "searchReady"))
        image = message.get(Image)[0]
        await update_user_called_data(group_id, sender, "search", 1)
        return await search_bangumi(group_id, sender, image.url)

    elif message_text == "rank":
        await update_total_calls_once("response")
        return await get_rank(group_id, app)

    # 爬虫相关功能
    """
    SAGIRI API相关功能：
        历史上的今天
    """
    if message_text == "历史上的今天":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_history_today()
    """
    热榜相关：
        微博热搜
        知乎热搜
        github热搜
    """
    if message_text == "weibo" or message_text == "微博":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 5)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_weibo_hot(group_id)

    if message_text == "zhihu" or message_text == "知乎":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 5)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_zhihu_hot(group_id)

    if message_text == "github热榜" or message_text == "github trend":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 6)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_github_hot(group_id)

    """
    B站相关功能:
        B站新番时间表
        B站直播间查询
    """
    if message_text[-4:] == "日内新番":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        num = message_text[:-4]
        if not num.isdigit() or int(num) <= 0 or int(num) > 7:
            return [
                At(target=sender),
                Plain(text="参数错误！必须为数字1-7！")
            ]
        else:
            return await formatted_output_bangumi(int(num), group_id)

    """
    力扣相关功能：
        用户信息查询
        每日一题查询
        具体题目查询
    """
    if message_text.startswith("leetcode "):
        await update_total_calls_once("response")
        return await get_leetcode_statics(message_text.replace("leetcode ", ""))

    """
    steam相关功能：
        steam游戏查询
    """
    if message_text.startswith("steam "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_steam_game_search(message_text.replace("steam ", ""))

    """
    douban相关功能：
        douban书籍推荐（tag）
    """
    if message_text.startswith("douban "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        tag = message_text[7:]
        if tag:
            return await get_book_recommand_by_tag(tag)
        else:
            return [
                "None",
                MessageChain.create([
                    Plain(text="你倒是说要什么标签的书籍啊！你这样子人家不知道搜什么了啦~")
                ])
            ]

    """
    bangumi相关功能：
        番剧查询
    """
    if message_text.startswith("番剧 "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 2)
            if frequency_limit_res:
                return frequency_limit_res

        keyword = message_text[3:]
        return await get_bangumi_info(sender, keyword)

    """
    其他功能:
        文本翻译
        点歌
        机器人帮助
        自动回复
        笑话
        群语录
        平安经（群人数过多时慎用）
        pornhub风格图片生成
        缩写
        获取磁力链
        搜索pdf
        年内报告
        月内报告
        签到
        996查询
        qrcode生成
        在线py环境
        摸~
    """
    if message.has(At) and message.get(At)[0].target == await get_config("BotQQ") and re.search(".*用.*怎么说",
                                                                                                message_text):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_translate(message_text, sender)

    elif message_text.startswith("点歌 ") and len(message_text) >= 4:

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 3)
            if frequency_limit_res:
                return frequency_limit_res

        print("search song:", message_text[3:])
        return await get_song_ordered(message_text[3:])

    if message_text == "help" or message_text == "!help" or message_text == "/help" or message_text == "！help":

        await update_total_calls_once("response")

        return [
            "None",
            MessageChain.create([
                Plain(text="点击链接查看帮助：http://doc.sagiri-web.com/web/#/p/7a0f42b15bbbda2d96869bbd8673d910\n"),
                Plain(text="文档尚未完善，功能说明还在陆续增加中！")
            ])
        ]

    if message_text == "教务通知":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_jlu_csw_notice(group_id)

    if re.search("来点.*笑话", message_text):
        await update_total_calls_once("response")
        joke_dict = {
            "苏联": "soviet",
            "法国": "french",
            "法兰西": "french",
            "美国": "america",
            "美利坚": "america"
        }
        name = re.findall(r'来点(.*?)笑话', message_text, re.S)
        if name == ['']:
            return [
                "None",
                MessageChain.create([
                    At(target=sender),
                    Plain(text="来点儿啥笑话啊，你又不告诉人家！哼！")
                ])
            ]
        elif name[0] in joke_dict.keys():
            msg = await get_key_joke(joke_dict[name[0]])
            await write_log("joke", "none", sender, group_id, True, "function")
            return msg
        else:
            msg = await get_joke(name[0])
            await write_log("joke", "none", sender, group_id, True, "function")
            return msg

    if message_text == "群语录":
        await update_total_calls_once("response")
        return await get_group_quotes(group_id, app, "None", "random", "None")
    elif re.search("来点.*语录", message_text):
        await update_total_calls_once("response")
        name = re.findall(r'来点(.*?)语录', message_text, re.S)[0]
        at_obj = message.get(At)
        if name == [] and at_obj == []:
            return ["None"]
        elif at_obj:
            at_str = at_obj[0].asSerializationString()
            member_id = re.findall(r'\[mirai:at:(.*?),@.*?\]', at_str, re.S)[0]
            await write_log("quotes", "None", sender, group_id, True, "function")
            if message_text[-4:] == ".all":
                return await get_group_quotes(group_id, app, member_id, "all", "memberId")
            else:
                return await get_group_quotes(group_id, app, member_id, "select", "memberId")
        elif name:
            await write_log("quotes", "None", sender, group_id, True, "function")
            if message_text[-4:] == ".all":
                return await get_group_quotes(group_id, app, name, "all", "nickname")
            else:
                return await get_group_quotes(group_id, app, name, "select", "nickname")

    if message_text == "平安":

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 6)
            if frequency_limit_res:
                return frequency_limit_res

        member_list = await app.memberList(group_id)
        msg = list()
        msg.append(Plain(text=f"群{message_info.sender.group.name}平安经\n"))
        for i in member_list:
            msg.append(Plain(text=f"{i.name}平安\n"))
        return [
            "None",
            MessageChain.create(msg)
        ]

    if message_text.startswith("ph ") and len(message_text.split(" ")) == 3:

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        if "\\" in message_text or "/" in message_text:
            return [
                "None",
                MessageChain.create([
                    Plain(text="不支持 '/' 与 '\\' ！")
                ])
            ]
        args = message_text.split(" ")
        left_text = args[1]
        right_text = args[2]
        path = f'./statics/temp/ph_{left_text}_{right_text}.png'
        if not os.path.exists(path):
            try:
                await make_ph_style_logo(left_text, right_text)
            except OSError as e:
                if "[Errno 22] Invalid argument:" in str(e):
                    return [
                        "quoteSource",
                        MessageChain.create([
                            Plain(text="非法字符！")
                        ])
                    ]
        return [
            "None",
            MessageChain.create([
                Image.fromLocalFile(path)
            ])
        ]

    if message_text.startswith("缩 "):

        await update_total_calls_once("response")

        abbreviation = message_text[2:]
        # print(abbreviation)
        if abbreviation.isalnum():
            return await get_abbreviation_explain(abbreviation, group_id)
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="只能包含数字及字母！")
                ])
            ]

    if message_text.startswith("magnet "):

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 6)
            if frequency_limit_res:
                return frequency_limit_res

        target = message_text[7:]
        if target:
            return await search_magnet(target, group_id)
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="请输入关键词！")
                ])
            ]

    if message_text.startswith("pdf ") or message_text.startswith("PDF "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 6)
            if frequency_limit_res:
                return frequency_limit_res

        keyword = message_text[4:]
        if keyword:
            return await search_pdf(group_id, keyword)
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="请输入关键词！")
                ])
            ]

    if message_text == "我的年内总结":
        await update_total_calls_once("response")
        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 6)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_personal_review(group_id, sender, "year")

    if message_text == "我的月内总结":
        await update_total_calls_once("response")
        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 6)
            if frequency_limit_res:
                return frequency_limit_res

        return await get_personal_review(group_id, sender, "month")

    if message_text == "本群年内总结" and sender == await get_config("HostQQ"):
        await update_total_calls_once("response")
        msg = await get_group_review(group_id, sender, "year")
        return msg

    if message_text == "本群月内总结" and sender == await get_config("HostQQ"):
        await update_total_calls_once("response")
        msg = await get_group_review(group_id, sender, "month")
        return msg

    if message.has(At) and message_text.startswith("摸") or message_text.startswith("摸 "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        target_id = message.get(At)[0].target
        await petpet(target_id)
        return [
            "None",
            MessageChain.create([
                Image.fromLocalFile(f'./statics/temp/tempPetPet-{target_id}.gif')
            ])
        ]

    if message_text.startswith("添加生日 "):
        await update_total_calls_once("response")
        birthday = message_text[5:]
        try:
            birthday = datetime.datetime.strptime(birthday, "%m-%d").strftime("%m-%d")
            await save_birthday(sender, group_id, birthday)
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text=f"用户: {sender}\n生日: {birthday}\n添加成功！")
                ])
            ]
        except Exception as e:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text=str(e)),
                    Plain(text="请检查格式！格式应为%m-%d的形式！")
                ])
            ]

    if message_text == "签到":
        await update_total_calls_once("response")
        return await register(group_id, sender)

    if message_text.startswith("996 "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        keyword = message_text[4:]

        if keyword:
            return await check996(keyword)
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="请输入关键词！")
                ])
            ]

    if message_text.startswith("qrcode "):

        await update_total_calls_once("response")

        if await get_setting(group_id, "countLimit"):
            frequency_limit_res = await limit_exceeded_judge(group_id, 1)
            if frequency_limit_res:
                return frequency_limit_res

        content = message_text[7:]
        if content:
            return await make_qrcode(content)
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="请输入要转为二维🐎的内容！")
                ])
            ]

    if re.search(r"super .*?:[\r\n]", message_text) and message_text.startswith("super "):
        if await get_setting(group_id, "compile"):
            language = re.findall(r"super (.*?):", message_text, re.S)[0]
            code = message_text[7 + len(language):]
            result = await network_compile(language, code)
            if isinstance(result, str):
                return [
                    "quoteSource",
                    MessageChain.create([
                        Plain(text=result)
                    ])
                ]
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text=result["output"] if result["output"] else result["errors"])
                ])
            ]
        else:
            return [
                "quoteSource",
                MessageChain.create([
                    Plain(text="网络编译器功能尚未开启哦~")
                ])
            ]

    auto_reply = await keyword_reply(message_text)
    if auto_reply:
        return auto_reply

    if message.has(At) and message.get(At)[0].target == await get_config("BotQQ"):
        await update_total_calls_once("response")
        return await reply_process(group_id, sender, message_text)
    return ["None"]
