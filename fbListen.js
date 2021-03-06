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
                                api.sendMessage("[MSGIX] ?????? : ????????????????????????????????????????????????" + username, destID);
                            } else {
                                api.sendMessage("[MSGIX] ?????? : ????????????????????????????????????" + username, destID);
                            }
                        } else if (message.body.includes("!Sync")) {
                            result = allowSync(message.senderID);
                            if (result) {
                            	api.sendMessage("[MSGIX] ?????? : ????????????????????????????????????????????????" + username, destID);
                            } else {
                            	api.sendMessage("[MSGIX] ?????? : ????????????????????????????????????" + username, destID);
                            }                         
                        } else if (message.body.includes("!Help")) {
                            result = dSyncExist(message.senderID);
                            var replyString = "";
                            if (result) {
                                replyString += "?????????????????????\n";
                                console.log(username + '??????????????????????????????');
                            } else {
                            	replyString += "?????????????????????\n";
                            	console.log(username + '???????????????????????????');
                            }
                            replyString += "!DontSync : ??????????????????????????????????????????\n";
		            replyString += "!Sync : ????????????????????????????????????\n";
		            replyString += "!Help : ???????????????????????????\n";
                            api.sendMessage(replyString, destID);
                        }
                    }
                    result = dSyncExist(message.senderID);
                    console.log(username + ' ???: ' + message.body);
                    if (result || command) {
                    	console.log(username + ' ??????????????????????????????');
                    } else {
		        var replyString = '[?????????] ' + username + ' ???: \n' + message.body;
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
