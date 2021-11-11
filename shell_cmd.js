var fs        = require('fs');
var http      = require('http');
var path      = require('path');
var WebSocket = require('ws');
var express   = require('express');
var pty       = require('pty.js');
var hbs       = require('hbs');
var dotenv    = require('dotenv');
var port      = process.env.PORT;
var token     = process.env.TOKEN;


// Create all your routes
var router = express.Router();
router.get('/', function (req, res) {
  res.redirect(req.baseUrl + '/tmux');
});
router.get('/tmux*', function (req, res) {
  res.render('index', { baseURI: req.baseUrl });
});
router.use(express.static(path.join(__dirname, 'public')));

// Setup app
var app = express();

// Setup template engine
app.set('view engine', 'hbs');
app.set('views', path.join(__dirname, 'views'));

// Mount the routes at the base URI
app.use(process.env.PASSENGER_BASE_URI || '/', router);

// Setup websocket server
var server = new http.createServer(app);
var wss = new WebSocket.Server({ server: server });

wss.on('connection', function connection (ws) {
  var match;
  var dir;
  var term;
  var cmd, args, cwd, env;

  console.log('Connection established');

  // Determine host and dir from request URL
  console.log(ws.upgradeReq.url);
  if (match = ws.upgradeReq.url.match(/.*?\/tmux\?token=(.*)$/)) {
    qtoken = match[2];
  } 

  if (! qtoken == token) {
    ws.close();
    return
  }


  cmd = process.argv[2];
  args = process.argv.slice(3);
    
  cwd = process.env.HOME;
  env = process.env;
  term = pty.spawn(cmd, args, {
    name: 'xterm-256color',
    cols: 80,
    rows: 30,
    cwd: cwd,
    env: env
  });

  console.log('Opened terminal: ' + term.pid);

  term.on('data', function (data) {
    ws.send(data, function (error) {
      if (error) console.log('Send error: ' + error.message);
    });
  });

  term.on('error', function (error) {
    ws.close();
  });

  term.on('close', function () {
    ws.close();
  });

  ws.on('message', function (msg) {
    msg = JSON.parse(msg);
    if (msg.input)  term.write(msg.input);
    if (msg.resize) term.resize(parseInt(msg.resize.cols), parseInt(msg.resize.rows));
  });

  ws.on('close', function () {
    term.end();
    console.log('Closed terminal: ' + term.pid);
  });
});
function noop() {}
const interval = setInterval(function ping() {
          wss.clients.forEach(function each(wsc) { wsc.ping(noop); });
}, 30000);


server.listen(port, function () {
  console.log('Listening on ' + port);
});
