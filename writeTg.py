import sys
import base64

from telethon import TelegramClient, events, sync
from tgInfo import getID, getHash, getChatID, getGroupID

tgClient = TelegramClient('msgix', getID(), getHash());

start = True
chatID = getChatID()

async def main():
    base64Msg = sys.argv[1]
    base64Bin = base64.b64decode(base64Msg)
    decodeMsg = base64Bin.decode('utf-8')
    #print(decodeMsg)
    #async for dialog in tgClient.iter_dialogs():
    #    print(dialog.name, 'has ID', dialog.id)
    await tgClient.send_message(getGroupID(), decodeMsg)

with tgClient:
    tgClient.loop.run_until_complete(main())