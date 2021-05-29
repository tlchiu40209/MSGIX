const login = require("facebook-chat-api");
const fs = require("fs");
const execSh = require("exec-sh");

const credential = { appState : JSON.parse(fs.readFileSync('appstate.json','utf-8'))}
// appstate.json is your bot account's facebook cookie.

const readFileLines = filename =>
    fs
        .readFileSync(filename)
        .toString('UTF8')
        .split('\n');

var syncList =  readFileLines('syncUserFB.txt');

function updateSyncFile() {
    const fileWriter = fs.createWriteStream('syncUserFB.txt', {
    	flags: 'w'
    });
    for (var i = 0; i < syncList.length; i++) {
    	fileWriter.write(syncList[i]);
    }
}

function dSyncExist(userID) {
    if (syncList.length == 0) {
        console.log("Sync List Empty");
        return false;
    }
    for (var i = 0; i < syncList.length; i++) {
    	if (userID == syncList[i]) {
    	    return true;
    	}
    }
}

function dontSync(userID) {
    if (syncList.length == 0) {
        console.log("Sync List Empty");
        syncList.push(userID);
        updateSyncFile();
        return true;
    }

    if (dSyncExist(userID)) {
        return false;
    } else {
        syncList.push(userID);
        updateSyncFile();
        return true;
    }
}

function removeArrayItem(arr) {
    var what, a = arguments, L = a.length, ax;
    while (L > 1 && arr.length){
        what = a[--L];
        while ((ax = arr.indexOf(what)) !== -1) {
            arr.splice(ax, 1);
        }
    }
    return arr;
}

function allowSync(userID) {
    if (syncList.length == 0) {
        return false;
    }

    if (dSyncExist(userID)) {
        syncList = removeArrayItem(syncList, userID);
        updateSyncFile();
        return true;
    } else {
        return false;
    }
}

function callTg(execString) {
    execSh(execString);
}

login(credential, (err, api)=>{
    if (err) return console.error(err);
    fs.writeFileSync('appstate.json', JSON.stringify(api.getAppState()));
    api.listenMqtt((err, message) =>{
        if (message.type == 'message' || message.type == 'message_reply') {
            var destID = "<YOUR_CHAT_ID_HERE>";
            //This is your Facebook Group Chat's Chat ID
            if (message.threadID == destID) {
                api.getUserInfo(message.senderID, (err, userInfo) => {
                    username = userInfo[message.senderID].name;
                    command = false;
                    if ("!" == message.body.charAt(0)) {
                        command = true;
                        if (message.body.includes("!DontSync")) {
                            result = dontSync(message.senderID);
                            if (result){
                                api.sendMessage("[MSGIX] 系統 : 已經為您的帳號停用訊息同步功能。" + username, destID);
                            } else {
                                api.sendMessage("[MSGIX] 系統 : 您已經停用訊息同步功能。" + username, destID);
                            }
                        } else if (message.body.includes("!Sync")) {
                            result = allowSync(message.senderID);
                            if (result) {
                            	api.sendMessage("[MSGIX] 系統 : 已經為您的帳號啟用訊息同步功能。" + username, destID);
                            } else {
                            	api.sendMessage("[MSGIX] 系統 : 您已經啟用訊息同步功能。" + username, destID);
                            }                         
                        } else if (message.body.includes("!Help")) {
                            result = dSyncExist(message.senderID);
                            var replyString = "";
                            if (result) {
                                replyString += "同步功能：關閉\n";
                                console.log(username + '自行要求不同步訊息。');
                            } else {
                            	replyString += "同步功能：開啟\n";
                            	console.log(username + '自行要求同步訊息。');
                            }
                            replyString += "!DontSync : 請不要同步接下來我傳送的訊息\n";
		            replyString += "!Sync : 請同步我接下來傳送的訊息\n";
		            replyString += "!Help : 帳號狀態與指令說明\n";
                            api.sendMessage(replyString, destID);
                        }
                    }
                    result = dSyncExist(message.senderID);
                    console.log(username + ' 說: ' + message.body);
                    if (result || command) {
                    	console.log(username + ' 決定不同步這條訊息。');
                    } else {
		        var replyString = '[福本市] ' + username + ' 說: \n' + message.body;
		        var b64String = new Buffer(replyString).toString('base64');
		        var execString = "python3 /home/mix/msgix/tgWriter.py " + b64String;
		        callTg(execString);
                    }
                });
            } else {
                console.log("Not belong to this group!")
            }            
        }
    });
});
