const login = require("facebook-chat-api");
const fs = require("fs")
global.atob = require("atob")

const credential = { appState : JSON.parse(fs.readFileSync('/home/mix/fbmix/appstate.json','utf-8'))}

var toFbMessage = new Buffer(process.argv[2], 'base64').toString('utf-8');
console.log(toFbMessage);

login(credential, (err, api)=>{
    if (err) return console.error(err);
    fs.writeFileSync('/home/mix/fbmix/appstate.json', JSON.stringify(api.getAppState()));
    var	destID = "<FB ID Here>";
    var	destMsg	= toFbMessage;
    api.sendMessage(destMsg, destID);
    tInfo = api.getThreadInfo(destID);
    console.log(tInfo)
});
