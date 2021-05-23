const login = require("facebook-chat-api");
const fs = require("fs");
const execSh = require("exec-sh");

const credential = { appState : JSON.parse(fs.readFileSync('/home/mix/fbmix/appstate.json','utf-8'))}

function callTg(execString) {
    execSh(execString);
}

login(credential, (err, api)=>{
    if (err) return console.error(err);
    fs.writeFileSync('/home/mix/fbmix/appstate.json', JSON.stringify(api.getAppState()));
    api.listenMqtt((err, message) =>{
        console.log(message);
        if (message.type == 'message' || message.type == 'message_reply') {
            var destID = "<FB ID Here>";
            if (message.threadID == destID) {
                api.getUserInfo(message.senderID, (err, userInfo) => {
                    //console.log(JSON.stringify(userInfo));
                    username = userInfo[message.senderID].name;
                    var replyString = '[福本市] ' + username + ' 說: \n' + message.body;
                    console.log(replyString);
                    var b64String = new Buffer(replyString).toString('base64');
                    console.log(b64String);
                    var execString = "python3 /home/mix/PycharmProjects/mixTelegram/writeTg.py " + b64String;
                    console.log(execString);
                    callTg(execString);
                });
            } else {
                console.log("Not belong to this group!")
            }            
        }
    });
});
