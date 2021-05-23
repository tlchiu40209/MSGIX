syncFile = open('syncUser.txt', 'r')
syncList = syncFile.readlines()
syncFile.close()

syncFileAdmin = open('syncBan.txt', 'r')
syncListAdmin = syncFileAdmin.readlines()
syncFileAdmin.close()

def dontSync(userID):
    global syncList
    if len(syncList) == 0:
        syncList.append(str(userID))
        updateSyncFile()
        return True

    if dSyncExist(userID):
        return False
    else:
        syncList.append(str(userID))
        updateSyncFile()
        return True


def banSync(userID):
    global syncListAdmin
    if len(syncListAdmin) == 0:
        syncListAdmin.append(str(userID))
        updateSyncFileAdmin()
        return True

    if dSyncAdminExist():
        return False
    else:
        syncListAdmin.append(str(userID))
        updateSyncFileAdmin()
        return True


def allowSync(userID):
    global syncList
    if len(syncList) == 0:
        print("Sync List Empty!")
        return False

    if dSyncExist(str(userID)):
        syncList.remove(str(userID))
        updateSyncFile()
        return True
    else:
        return False


def unbanSync(userID):
    global syncListAdmin
    if len(syncListAdmin) == 0:
        print("Sync List Empty")
        return False

    if dSyncAdminExist(str(userID)):
        syncListAdmin.remove(str(userID))
        updateSyncFileAdmin()
        return True
    else:
        return False


def dSyncExist(userID):
    global syncList
    if len(syncList) == 0:
        print("Sync List Empty!")
        return False

    for syncID in syncList:
        if syncID == str(userID):
            return True

    return False


def dSyncAdminExist(userID):
    global syncListAdmin
    if len(syncListAdmin) == 0:
        print("Sync List Admin Empty!")
        return False

    for syncIDAdmin in syncListAdmin:
        if syncIDAdmin == str(userID):
            return True

    return False


def updateSyncFile():
    global syncList
    syncFile = open('syncUser.txt', 'w')
    syncFile.writelines(syncList)
    syncFile.close()


def updateSyncFileAdmin():
    global syncListAdmin
    syncFileAdmin = open('syncBan.txt', 'w')
    syncFileAdmin.writelines(syncListAdmin)
    syncFileAdmin.close()