# -*- coding: utf-8 -*-
import asyncio
import json
import os
import random

import aiohttp
from graia.application import GraiaMiraiApplication as Mirai
from graia.application import Session
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.exceptions import *
from graia.application.message.elements.internal import (
    App, At, Image, Plain)
from graia.broadcast import Broadcast
from graia.scheduler import GraiaScheduler

import MOEBOT.basics.card_api as card_api
import MOEBOT.basics.card_user as card_user
from MOEBOT.basics.get_config import get_config
from MOEBOT.basics.tools import make_card

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
sche = GraiaScheduler(loop=loop, broadcast=bcc)
with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
    configs = json.loads(f.read())
app = Mirai(
    broadcast=bcc,
    connect_info=Session(
        host=configs["miraiHost"],
        authKey=configs["authKey"],
        account=configs["BotQQ"],
        websocket=True
    )
)


@bcc.receiver("GroupMessage")
async def group_message_listener(
    app: Mirai,
    group: Group,
    member: Member,
    message: MessageChain
):
    if message.asDisplay().startswith("查询记录"):
        r = await card_api.searchlog()
        if r["code"] == 1:
            news = ""
            for i in r["data"]:
                if i["type"] == "dailyCard":
                    news += "\n%s抽中了出自《%s》的%s星卡%s" % (
                        i["nickName"], i["data"]["title"], i["data"]["star"], i["data"]["name"])
                elif i["type"] == "register":
                    news += "\n萌新%s加入萌物世界" % i["nickName"]
                elif i["type"] == "battle":
                    news += "%s在卡牌对战中战胜了%s，共获得了%s点竞技点和%s点经验值。" % (
                        i["nickName"], i["data"]["EmName"], i["data"]["getScore"], i["data"]["getExp"])
            msg = message.create([
                At(target=member.id),
                Plain("查询结果如下%s" % news)
            ])
        else:
            msg = message.create([
                At(target=member.id),
                Plain(r["msg"])
            ])
        await app.sendGroupMessage(group, msg)

    elif "抽卡" in message.asDisplay():
        email = card_user.searchinfo(member.id)["email"]
        if len(message.asDisplay()) != 3:
            r = {'code': 0, 'msg': '指令有误！正确格式：[抽卡+序号]'}
        elif message.asDisplay() == "抽卡1":
            r = await card_api.dailycard(email, 0, "0")
        else:
            sel = (int(message.asDisplay()[2:3]) - 1 or 0)
            r = await card_api.dailycard(email, sel, "0")
        if r["code"] == 1:
            make_card(r["packageId"], r["cardChoiseList"][0], r["cardChoiseList"][1], r["cardChoiseList"][2],
                      r["choiseIndex"], r["isNew"])
            msg = message.create([
                At(target=member.id),
                Plain("抽卡成功! 还剩%s次机会" % r["leftGetChance"]),
                Image.fromLocalFile("temp/card.jpg")
            ])
        elif r["code"] == 2:
            msg = message.create([
                At(target=member.id),
                Plain("您还未注册哟(＾Ｕ＾)ノ~\n发送[注册]开始您的萌物之旅吧")
            ])
        else:
            msg = message.create([
                At(target=member.id),
                Plain(r["msg"])
            ])
        await app.sendGroupMessage(group, msg)

    elif message.asDisplay() == "注册":
        msg = message.create([
            At(target=member.id),
            Plain(''' 准备好进入萌物世界了吗
您有多种注册方式
1. 前往http://116.85.72.173:3000进行注册
2. 私聊我在线注册
3. 发送 “快速注册 [昵称]”进行注册. 个人信息将会以私聊形式发送给您
''')])
        await app.sendGroupMessage(group, msg)

    elif message.asDisplay()[:5] == "快速注册 ":
        if card_user.searchinfo(member.id) != -1:
            await app.sendGroupMessage(group, message.create([
                At(target=member.id),
                Plain("您已注册！"),
            ]))
        else:
            email = str(member.id) + "@qq.com"
            password = random.choice(['miaow', 'moecard'])
            nickName = message.asDisplay().partition(' ')[2]
            r = await card_api.reg(email, password, nickName)
            if r["code"] == 1:
                msg = message.create([
                    At(target=member.id),
                    Plain("注册成功!"),
                ])
                card_user.newuser(member.id, email)
                await app.sendGroupMessage(group, msg)
                await app.sendFriendMessage(message.sender, message.create([
                    Plain('''
尊敬的%s大人：
这是通往萌物世界的令牌，请查收
email：%s
password：%s
''' % (nickName, email, password))]))
            else:
                msg = message.create([
                    At(target=member.id),
                    Plain(r["msg"]),
                ])
                await app.sendGroupMessage(group, msg)


'''
    elif message.asDisplay().startswith("一言"):
        await app.sendGroupMessage(group, message.create([
            At(target=member.id),
            Image.fromLocalFile("%s/public/OneText/%s.jpg" %
                                (home, random.randint(0, 18)))
        ]))
'''

autoreply = False


@bcc.receiver("GroupMessage")
async def group_message_listener(
    app: Mirai,
    group: Group,
    member: Member,
    message: MessageChain
):
    async def moli(word):
        api_key = "57d8d9ecdc643f69906c541ec64d3fb9"
        api_secret = "Miaow"
        url = "http://i.itpk.cn/api.php?limit=4&api_key=%s&api_secret=%s&question=%s" % (
            api_key, api_secret, word)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url) as r:
                if r.status == 200:
                    return await r.read()
                else:
                    return random.choice(["喵喵酱现在不想和你说话", "喵喵酱还在睡觉呢"])

    global autoreply
    if message.asDisplay() in ('喵喵起床', '/on'):
        autoreply = True
        await app.sendGroupMessage(group, message.create([
            Plain("喵喵酱已经醒了w")
        ]))
    elif message.asDisplay() in ('喵喵睡觉', '喵喵闭嘴', '/off'):
        autoreply = False
        await app.sendGroupMessage(group, message.create([
            Plain("喵喵酱已经睡了w")
        ]))
    elif autoreply:
        await app.sendGroupMessage(group, message.create([
            At(target=member.id),
            Plain(" " + await moli(message.asDisplay()))
        ]))


@bcc.receiver("GroupMessage")
async def group_message_listener(
        app: Mirai,
        group: Group,
        member: Member,
        message: MessageChain
):
    print("接收到组%s中来自%s的消息:%s" %
          (group.name, member.name, message.asDisplay()))

    if message.asDisplay() == "start old version" and member.id == await get_config("HostQQ"):
        await app.sendGroupMessage(group, message.create([Plain(text="即将切换至旧版本...")]))
        await app.sendGroupMessage(group, message.create([Plain(text="切换成功！")]))
        os.system("%s \"%s\"" % (await get_config("environment"), await get_config("oldVersion")))

    if message.asDisplay() == "restart bot" and member.id == await get_config("HostQQ"):
        await app.sendGroupMessage(group, message.create([Plain(text="即将重启机器人...")]))
        await app.sendGroupMessage(group, message.create([Plain(text="重启成功！")]))
        os.system("%s \"%s\"" % (await get_config("environment"), await get_config("newVersion")))

    if message.asDisplay() == "bot shutdown" and member.id == await get_config("HostQQ"):
        await app.sendGroupMessage(group, message.create([Plain(text="即将退出机器人...")]))
        exit(0)

    if message.asDisplay() == "pc shutdown" and member.id == await get_config("HostQQ"):
        await app.sendGroupMessage(group, message.create([Plain(text="即将关机...")]))
        os.system("shutdown -s")

    if message.asDisplay() == "Ai off" and member.id == await get_config("HostQQ"):
        await app.sendGroupMessage(group, message.create([Plain(text="即将关机...")]))
        os.system("shutdown -s")

    if message.asDisplay() == "test2" and member.id == await get_config("HostQQ"):
        welcome_json = """
                {
                    "prompt": "欢迎入群",
                    "sourceUrl": "",
                    "extraApps": [],
                    "appID": "",
                    "sourceName": "",
                    "desc": "",
                    "app": "com.tencent.miniapp",
                    "config": {
                        "forward": true
                    },
                    "ver": "1.0.0.89",
                    "view": "all",
                    "meta": {
                        "all": {
                            "preview": "http:/gchat.qpic.cn/gchatpic_new/12904366/1030673292-3125245045-E7FCC807BECA2938EBE5D57E7E4980FF/0?term=2",
                            "title": "欢迎入群",
                            "buttons": [{
                                "name": "---FROM SAGIRI-BOT---",
                                "action": "http://www.qq.com"
                            }],
                            "jumpUrl": "",
                            "summary": "欢迎进群呐~进群了就不许走了呐~\r\n"
                        }
                    },
                    "actionData": "",
                    "actionData_A": ""
                }"""
        print(("test2"))
        await app.sendGroupMessage(
            group.id, MessageChain.create([
                App(content=welcome_json)
            ])
        )


@bcc.receiver("MemberJoinEvent")
async def member_join(
        app: Mirai,
        event: MemberJoinEvent
):
    try:
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                At(target=event.member.id),
                Plain(text="我是本群小可爱纱雾哟~欢迎呐~一起快活鸭~")
            ])
        )
        # welcome_json = json.dumps(eval(await get_json_code("MemberJoinEvent")))
        # print(welcome_json)
        # welcome_json = """{
        #             "prompt": "[欢迎入群]",
        #             "extraApps": [],
        #             "sourceUrl": "",
        #             "appID": "",
        #             "sourceName": "",
        #             "desc": "",
        #             "app": "com.tencent.qqpay.qqmp.groupmsg",
        #             "ver": "1.0.0.7",
        #             "view": "groupPushView",
        #             "meta": {
        #                 "groupPushData": {
        #                     "fromIcon": "",
        #                     "fromName": "name",
        #                     "time": "",
        #                     "report_url": "http:\\/\\/kf.qq.com\\/faq\\/180522RRRVvE180522NzuuYB.html",
        #                     "cancel_url": "http:\\/\\/www.baidu.com",
        #                     "summaryTxt": "",
        #                     "bannerTxt": "欸嘿~欢迎进群呐~进来了就不许走了哦~",
        #                     "item1Img": "",
        #                     "bannerLink": "",
        #                     "bannerImg": "http:\\/\\/gchat.qpic.cn\\/gchatpic_new\\/12904366\\/1046209507-2584598286-E7FCC807BECA2938EBE5D57E7E4980FF\\/0?term=2"
        #                 }
        #             },
        #             "actionData": "",
        #             "actionData_A": ""
        #         }"""
        welcome_json = """
        {
            "prompt": "SAGIRI",
            "sourceUrl": "",
            "extraApps": [],
            "appID": "",
            "sourceName": "",
            "desc": "",
            "app": "com.tencent.miniapp",
            "config": {
                "forward": true
            },
            "ver": "1.0.0.89",
            "view": "all",
            "meta": {
                "all": {
                    "preview": "http:\/\/gchat.qpic.cn\/gchatpic_new\/12904366\/1030673292-3125245045-E7FCC807BECA2938EBE5D57E7E4980FF\/0?term=2",
                    "title": "欢迎入群",
                    "buttons": [{
                        "name": "---FROM SAGIRI-BOT---",
                        "action": "http:\/\/www.qq.com"
                    }],
                    "jumpUrl": "",
                    "summary": "欢迎进群呐~进群了就不许走了呐~\r\n"
                }
            },
            "actionData": "",
            "actionData_A": ""
        }"""
        test_json = """
            {
                "app": "com.tencent.mannounce",
                "config": {
                    "ctime": 1610424762,
                    "forward": 0,
                    "token": "190bcca54b1eb9c543676aa1c82762ab"
                },
                "desc": "群公告",
                "extra": {
                    "app_type": 1,
                    "appid": 1101236949,
                    "uin": 1900384123
                },
                "meta": {
                    "mannounce": {
                        "cr": 1,
                        "encode": 1,
                        "fid": "93206d3900000000ba21fd5fa58a0500",
                        "gc": "963453075",
                        "sign": "cbbf90a7cbf1dc938ac5bdb8224fc3cb",
                        "text": "dGVzdA==",
                        "title": "576k5YWs5ZGK",
                        "tw": 1,
                        "uin": "1900384123"
                    }
                },
                "prompt": "[群公告]test",
                "ver": "1.0.0.43",
                "view": "main"
            }"""
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                App(content=welcome_json)
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("MemberLeaveEventQuit")
async def member_leave(app: Mirai, event: MemberLeaveEventQuit):
    try:
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                Plain(text="%s怎么走了呐~是因为偷袭了69岁的老同志吗嘤嘤嘤" % event.member.name)
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("MemberMuteEvent")
async def member_muted(app: Mirai, event: MemberMuteEvent):
    if event.operator is not None:
        if event.member.id == await get_config("HostQQ"):
            try:
                await app.unmute(event.member.group.id, event.member.id)
                await app.sendGroupMessage(
                    event.member.group.id, MessageChain.create([
                        Plain(text="保护！保护！")
                    ])
                )
            except PermissionError:
                pass
        else:
            try:
                m, s = divmod(event.durationSeconds, 60)
                h, m = divmod(m, 60)
                await app.sendGroupMessage(
                    event.member.group.id, MessageChain.create([
                        Plain(text="哦~看看是谁被关进小黑屋了？\n"),
                        Plain(text="哦我的上帝啊~是%s！他将在小黑屋里呆%s哦~" %
                              (event.member.name, "%02d:%02d:%02d" % (h, m, s)))
                    ])
                )
            except AccountMuted:
                pass


@bcc.receiver("MemberUnmuteEvent")
async def member_unmuted(app: Mirai, event: MemberUnmuteEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                Plain(text="啊嘞嘞？%s被放出来了呢~" % event.member.name)
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("MemberLeaveEventKick")
async def member_kicked(app: Mirai, event: MemberLeaveEventKick):
    try:
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                Plain(text="%s滚蛋了呐~" % event.member.name)
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("MemberSpecialTitleChangeEvent")
async def member_special_title_change(app: Mirai, event: MemberSpecialTitleChangeEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                Plain(text="啊嘞嘞？%s的群头衔从%s变成%s了呐~" %
                      (event.member.name, event.origin, event.current))
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("MemberPermissionChangeEvent")
async def member_permission_change(app: Mirai, event: MemberPermissionChangeEvent):
    try:
        await app.sendGroupMessage(
            event.member.group.id, MessageChain.create([
                Plain(text="啊嘞嘞？%s的权限变成%s了呐~跪舔大佬！" %
                      (event.member.name, event.current))
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("BotLeaveEventKick")
async def bot_leave_group(app: Mirai, event: BotLeaveEventKick):
    print("bot has been kicked!")
    await app.sendFriendMessage(
        await get_config("HostQQ"), MessageChain.create([
            Plain(text=f"呜呜呜主人我被踢出{event.group.name}群了")
        ])
    )


@bcc.receiver("GroupNameChangeEvent")
async def group_name_changed(app: Mirai, event: GroupNameChangeEvent):
    try:
        await app.sendGroupMessage(
            event.group, MessageChain.create([
                Plain(
                    text=f"群名改变啦！告别过去，迎接未来哟~\n本群名称由{event.origin}变为{event.current}辣！")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("GroupEntranceAnnouncementChangeEvent")
async def group_entrance_announcement_changed(app: Mirai, event: GroupEntranceAnnouncementChangeEvent):
    try:
        await app.sendGroupMessage(
            event.group, MessageChain.create([
                Plain(
                    text=f"入群公告改变啦！注意查看呐~\n原公告：{event.origin}\n新公告：{event.current}")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("GroupAllowAnonymousChatEvent")
async def group_allow_anonymous_chat_changed(app: Mirai, event: GroupAllowAnonymousChatEvent):
    try:
        await app.sendGroupMessage(
            event.group, MessageChain.create([
                Plain(
                    text=f"匿名功能现在{'开启辣！畅所欲言吧！' if event.current else '关闭辣！光明正大做人吧！'}")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("GroupAllowConfessTalkEvent")
async def group_allow_confess_talk_changed(app: Mirai, event: GroupAllowConfessTalkEvent):
    try:
        await app.sendGroupMessage(
            event.group, MessageChain.create([
                Plain(
                    text=f"坦白说功能现在{'开启辣！快来让大家更加了解你吧！' if event.current else '关闭辣！有时候也要给自己留点小秘密哟~'}")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("GroupAllowMemberInviteEvent")
async def group_allow_member_invite_changed(app: Mirai, event: GroupAllowMemberInviteEvent):
    try:
        await app.sendGroupMessage(
            event.group, MessageChain.create([
                Plain(
                    text=f"现在{'允许邀请成员加入辣！快把朋友拉进来玩叭！' if event.current else '不允许邀请成员加入辣！要注意哦~'}")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("MemberCardChangeEvent")
async def member_card_changed(app: Mirai, event: MemberCardChangeEvent, group: Group):
    try:
        await app.sendGroupMessage(
            group, MessageChain.create([
                Plain(
                    text=f"啊嘞嘞？{event.member.name}的群名片被{event.operator.name}从{event.origin}改为{event.current}了呢！")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("NewFriendRequestEvent")
async def new_friend_request(app: Mirai, event: NewFriendRequestEvent):
    await app.sendFriendMessage(
        await get_config("HostQQ"), MessageChain.create([
            Plain(text=f"主人主人，有个人来加我好友啦！\n"),
            Plain(text=f"ID：{event.supplicant}\n"),
            Plain(text=f"来自：{event.nickname}\n"),
            Plain(text=f"描述：{event.message}\n"),
            Plain(text=f"source：{event.sourceGroup}")
        ])
    )


@bcc.receiver("MemberJoinRequestEvent")
async def new_member_join_request(app: Mirai, event: MemberJoinRequestEvent):
    try:
        await app.sendGroupMessage(
            event.groupId, MessageChain.create([
                Plain(text=f"有个新的加群加群请求哟~管理员们快去看看叭！\n"),
                Plain(text=f"ID：{event.supplicant}\n"),
                Plain(text=f"昵称：{event.nickname}\n"),
                Plain(text=f"描述：{event.message}\n")
            ])
        )
    except AccountMuted:
        pass


@bcc.receiver("BotInvitedJoinGroupRequestEvent")
async def bot_invited_join_group(app: Mirai, event: BotInvitedJoinGroupRequestEvent):
    if event.supplicant != await get_config("HostQQ"):
        await app.sendFriendMessage(
            await get_config("HostQQ"), MessageChain.create([
                Plain(text=f"主人主人，有个人拉我进群啦！\n"),
                Plain(text=f"ID：{event.supplicant}\n"),
                Plain(text=f"来自：{event.nickname}\n"),
                Plain(text=f"描述：{event.message}\n")
            ])
        )


app.launch_blocking()
