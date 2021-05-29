const login = require("facebook-chat-api");
var net = require('net');
const fs = require("fs")
global.atob = require("atob")

const credential = { appState : JSON.parse(fs.readFileSync('appstate.json','utf-8'))}
// Appstate.json is your bot's Facebook cookie. Remember to change "name" to "key"

login(credential, (err, api)=>{
    if (err) return console.error(err);

    var destID = "YOUR_ID_HERE";
    // This is an ID from Facebook Group Chat.

    var server = net.createServer(client => {
        chunks = [];
        console.log('fbWrite 已經連線。');
        client.setEncoding('utf8');

        client.on('end', () => {
            console.log('fbWrite 已經斷線。')
        });

        client.on('data', chunk => {
            chunks.push(chunk);
            if (chunk.match(/\r\n$/)) {
                rawData = chunks.join('');
                message = new Buffer(rawData, 'base64').toString('utf-8');
                console.log('收到資料 : ' + message);
                api.sendMessage(message, destID);
                chunks = [];
            }
        });
    });

    server.on('listening', () => {
        console.log('fbWrite 等待輸入中。');
    });

    server.listen('fbWrite.sock');
});
