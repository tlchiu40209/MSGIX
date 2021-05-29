from telethon import TelegramClient, events, sync
from telethon.tl.types import ChannelParticipantsAdmins

from tgInfo import getID, getHash, getChatID
from tgSyncer import dontSync, banSync, allowSync, unbanSync, dSyncExist, dSyncAdminExist

import base64
import os

import socket

fbWriterAddress = 'fbWrite.sock'
fbWriter = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
fbWriter.connect(fbWriterAddress)

tgClient = TelegramClient('msgix', getID(), getHash());

start = True
chatID = getChatID()

@tgClient.on(events.NewMessage)
async def unreadMsgHandler(event):

    global start
    global chatID
    isCommanding = False
    requirePrefix = False
    chat = await event.get_chat()

    client_entity = await event.client.get_entity(event.from_id)
    name = client_entity.first_name.strip()
    adminIds = []
    userIdl = {}

    adminList = tgClient.iter_participants(getChatID(), filter=ChannelParticipantsAdmins)
    async for participant in adminList:
        adminIds.append(participant.id)

    userList = tgClient.iter_participants(getChatID())
    async for user in userList:
        #print(user)
        if user.username is None:
            continue
        else:
            userIdl['@' + user.username] = user.id

    if client_entity.last_name is not None:
        name = name + ' ' + client_entity.last_name.strip()
    #print(event)
    #print(client_entity)
    if event.text is None:
        print(name, '送了一則空訊息')
        return

    print(name, '說', event.text)

    #if testRun:
    #    await event.reply('[MSGIX] SYS : RCV : ' + event.text + ' FROM ' + client_entity.first_name.strip() + ' ' + client_entity.last_name.strip())

    if event.text[0] == '!':
        isCommanding = True
        if "!Start" in event.text:
            isAdmin = False
            for aids in adminIds:
                if aids == client_entity.id:
                    isAdmin = True
            if isAdmin:
                await event.reply('[MSGIX] 系統 : 啟動！')
                print(name, '要求啟動。')
                start = True
            else:
                await event.reply('[MSGIX] 系統 : 您沒有權限執行這項功能。')
                print(name, '試圖執行管理員功能，回報。')

        #if "!Test run" in event.text: #Should be deprecated soon
        #    await event.reply('[MSGIX] 系統 : 測試啟動！')
        #    print(name, '要求進行測試。')
        #    start = True


        if "!Shutdown" in event.text:
            isAdmin = False
            for aids in adminIds:
                if aids == client_entity.id:
                    isAdmin = True
            if isAdmin:
                await event.reply('[MSGIX] 系統 : 正常停止，再見！')
                print(name, '要求停止。')
                start = False
            else:
                await event.reply('[MSGIX] 系統 : 您沒有權限執行這項功能。')
                print(name, '試圖執行管理員功能，回報。')

        if "!Help" in event.text:
            #await event.reply('[MSGIX] 系統 : 指令說明列表建構中。')
            replyString = "[MSGIX] 系統 : 帳號狀態與指令說明：\n"
            if dSyncExist(client_entity.id):
                replyString += "同步功能：關閉\n"
            else:
                replyString += "同步功能：開啟\n"

            if dSyncAdminExist(client_entity.id):
                replyString += "管理員禁止同步：是\n"
            else:
                replyString += "管理員禁止同步：否\n"
            replyString += "!DontSync : 請不要同步接下來我傳送的訊息\n"
            replyString += "!Sync : 請同步我接下來傳送的訊息\n"
            replyString += "!BanSync @使用者 : (管理員) 禁止使用者使用同步功能\n"
            replyString += "!AllowSync @使用者 : (管理員) 解除禁止使用者使用同步功能\n"
            replyString += "!Help : 帳號狀態與指令說明\n"
            replyString += "!Sp : 強制送出這張圖(禁止R18!)\n"
            if requirePrefix:
                replyString += ":dc (或：迪西) : 同步該訊息到DC\n"
                replyString += ":fb (或：福本) : 同步該訊息到FB\n"
            await event.reply(replyString)
            print(name, '要求了自己的狀態跟說明。')

        if "!DontSync" in event.text:
            if dontSync(client_entity.id):
                await event.reply('[MSGIX] 系統 : 已經為您的帳號停用訊息同步功能。' + name);
                print(name, '自行要求不同步訊息。')
            else:
                await event.reply('[MSGIX] 系統 : 您已經停用訊息同步功能。')

        if "!Sync" in event.text:
            if allowSync(client_entity.id):
                await event.reply('[MSGIX] 系統 : 已經為您的帳號啟用訊息同步功能。' + name);
                print(name, '自行要求同步訊息。')
            else:
                await event.reply('[MSGIX] 系統 : 您已經啟用訊息同步功能。')

        if "!BanSync" in event.text:
            isAdmin = False
            for aids in adminIds:
                if aids == client_entity.id:
                    isAdmin = True

            if isAdmin:
                textParse = event.text.split(" ")
                if len(textParse) < 2:
                    await event.reply('[MSGIX] 系統 : 不正確的指令。')
                else:
                    destUserName = textParse[1]
                    if '@' in destUserName:
                        if destUserName in userIdl:
                            destUser = userIdl[destUserName]

                            for aids in adminIds:
                                if aids == destUser:
                                    await event.reply('[MSGIX] 系統 : 不能禁止管理員，請先將該使用者降級。')
                                    print(name, '試圖禁止其他管理員，回報。')
                                    return

                            if banSync(destUser):
                                await event.reply('[MSGIX] 系統 : 使用者被管理員禁止使用同步功能。')
                                print(name, '使用者', destUserName, '被管理員禁止使用同步功能。')
                            else:
                                await event.reply('[MSGIX] 系統 : 該名使用者已經被管理員禁止使用同步功能。')
                        else:
                            await event.reply('[MSGIX] 系統 : 找不到指定使用者。')
                    else:
                        await event.reply('[MSGIX] 系統 : 不正確的指令。')
            else:
                await event.reply('[MSGIX] 系統 : 您沒有權限執行這項功能。')
                print(name, '試圖執行管理員功能，回報。')

        if "!UnbanSync" in event.text:
            isAdmin = False
            for aids in adminIds:
                if aids == client_entity.id:
                    isAdmin = True

            if isAdmin:
                textParse = event.text.split(" ")
                if len(textParse) < 2:
                    await event.reply('[MSGIX] 系統 : 不正確的指令。')
                else:
                    destUserName = textParse[1]
                    if '@' in destUserName:
                        if destUserName in userIdl:
                            destUser = userIdl[destUserName];
                            if unbanSync(destUser):
                                await event.reply('[MSGIX] 系統 : 管理原已解除對使用者的禁止使用同步功能。')
                                print(name, '使用者', destUserName, '被管理員解除禁止使用同步功能。')
                            else:
                                await event.reply('[MSGIX] 系統 : 這個使用者沒有被管理員禁止使用同步功能。')
                        else:
                            await event.reply('[MSGIX] 系統 : 找不到指定使用者。')
                    else:
                        await event.reply('[MSGIX] 系統 : 不正確的指令。')
            else:
                await event.reply('[MSGIX] 系統 : 您沒有權限執行這項功能。')
                print(name, '試圖執行管理員功能，回報。')

    if start & isCommanding==False:
        #Forwarder preventing
        notValid = False
        if chatID != chat.id:
            print('收到了新訊息，但不是來自玄義獸國的訊息。')
            notValid = True
            return

        if not event.text:
            print('使用者', name, '發了空白訊息。')
            notValid = True
            return

        fwdPrevent = {"[福本市]", "[土公市]"}
        fwdHead = event.text[0:5]
        for fwdCheck in fwdPrevent:
            if fwdHead == fwdCheck:
                print('機器人無限迴圈保護機制啟動。')
                notValid = True
                return

        if requirePrefix is True and notValid is False:
            destStr = event.text[0:3]
            destMsg = '[土公市] ' + name + ' 説: \n' + event.text[4:]
            #replyString = '[土公市] ' + name + ' 説: ' + event.text
            if dSyncExist(client_entity.id):
                print('使用者', name, '決定不同步這條訊息。')
                return
            if dSyncAdminExist(client_entity.id):
                print('使用者', name, '已經被管理員禁止使用同步功能。')
                return
            if destStr == ':dc' or destStr == '：迪西':
                print('使用者', name, '將這條訊息同步到DC')
                print('這個功能還沒有實作')
                # Not implemented
            elif destStr == ':fb' or destStr == '：福本':
                print('使用者', name, '將這條訊息同步到FB')
                prepareResponse = destMsg.encode('utf-8')
                replyStringB64 = base64.b64encode(prepareResponse)
                #print(replyStringB64)
                #replyStringB64Str = replyStringB64.decode('ascii')
                #os.system('node /home/mix/fbmix/fbWrite.js ' + replyStringB64Str)
                fbWriter.send(replyStringB64)
                fbWriter.send(b"\r\n")
                #await event.reply(replyString)
            else:
                print('使用者', name, '沒指定同步地點')
        elif requirePrefix is False & notValid is False:
            if dSyncExist(client_entity.id):
                print('使用者', name, '決定不同步這條訊息。')
                return
            if dSyncAdminExist(client_entity.id):
                print('使用者', name, '已經被管理員禁止使用同步功能。')
                return
            print('使用者', name, '將這條訊息同步到FB')
            replyString = '[土公市] ' + name + ' 説: \n' + event.text
            prepareResponse = replyString.encode('utf-8')
            replyStringB64 = base64.b64encode(prepareResponse)
            # print(replyStringB64)
            #replyStringB64Str = replyStringB64.decode('ascii')
            #os.system('node /home/mix/fbmix/fbWrite.js ' + replyStringB64Str)
            fbWriter.send(replyStringB64)
            fbWriter.send(b"\r\n")
            # await event.reply(replyString)
        else:
            print('使用者', name, '發了系統不接受的訊息。')

tgClient.start()
tgClient.run_until_disconnected()
