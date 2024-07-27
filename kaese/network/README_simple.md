# Draft for simple Network Protocol for Käsekästchen

A Server shall listen to connections on port `2345/tcp`. Clients may connect to this port.


### Connect

When a new client connects, the server creates a new thread for this connection and
sends a `WelcomeMsg` (byte stream of json representation of the object). The server
may also send a `ConnectionErrorMsg` and close the connection if for example the maximum
number of connections is exceeded or a certain IP is block listed.


### Start a Game

As soon as two players are connected to the server, a new game starts and the servers sends both clients
a `GameStateMsg`.


### Play a Game

While a game is running, the client should render incoming `GameStateMsg`s. The client may request
a recent game state with a `RequestGameStateMsg`. A `GameStateMsg` contains:
 * who is Player1, who is Player2
 * a serializable version of the Gameboard object with its Boxes.
 * last_move, current player, wincounter, winner, ...
 * optional a game history

How to handle History? If sent by server, make it "scrollable", if not do not track it.

If it is the clients turn, the client should send a `MoveMsg`.

The server should answer with a new GameState or a `InvalidMoveErrorMsg`.


### Game ended
...


## Server

### CLI Parameter

```
  --listen IP (default to all interfaces)
  --port PORT (default 2345)
  --name NAME (default "Käsekästchen-Server")
  --max-connections...
  --size-x and --size-y
  --maybe a filename to load from for new games
```

A global Msg-In-Queue and Msg-Out-Queue for each connection shall be implemented.

All connection treads write received data to the single Msg-In-Queue and read from their
individual Msg-Out-Queue data that should be sent to the client.

The main thread of the server will take care of new connections. A separate server thread
handles the heavy load of reading the global Msg-In-Queue and writing appropriate objects
to the related individual Msg-Out-Queues.

The server decides all game details like who is Player 1, gameboard size, restarting or
loading a game. Maybe implement a simple local cli console to be able to issue commands to
the server.

```
/start x y
/swap players
/load filename
```



## Client

### CLI Parameter

```
  --server IP (default to all interfaces)
  --port PORT (default 2345)
  --name NAME (default "Player RANDOM_NUMBER")
  --session-id STRING or INT indicating the number of the key in the list in the local config file
```



## Keepalive

All clients shall send a `KeepAliveMsg` every 5 seconds to the server.

The server shall reply with a `KeepAliveAckMsg` as soon as possible.

If the Server haven't received a `KeepAliveMsg` from a certain client
for more than 30 seconds, it should terminate that connection.
