# Draft Network Protocol for Käsekästchen

A Server shall listen to connections on port `2345/tcp`. Clients may connect to this port.


### Connect

When a new client connects, the server creates a new thread for this connection and
sends a `PleaseIdentifyMsg` (byte stream of json representation of the object) which contains
the name of the server and the IP and port of the client as seen by the server. The server
may also send a `ConnectionErrorMsg` and close the connection if for example the maximum
number of connections is exceeded or a certain IP or `client_identification_id` is block listed.


### Identify / "Authenticate"

The client shall reply with a `IdentificationMsg` which contains the name of the player
and a `client_identification_id`. The `client_identification_id` shall be a random string created
by the client on its first run and should be stored in its local config files to be reused
for later connections.

The server shall reply with a `IdentificationAcknowledgedMsg` which contains the name
of the player as chosen by the server.

The server should use the name given by the client in the `IdentificationMsg`.

If the name was empty, the server shall create a random one or preferably use the one last
used by the given `client_identification_id`. 

If the name is already in use by another `client_identification_id`, the server
should append a random number to the given name.

If there is a session for the given `client_identification_id`, but the name does not match,
server shall update the name of the user in that session with the suggested one (maybe
extended with a random number to avoid duplicates).



What if more than one client with same id connects at the same time?
Duplicate messages to all of them and accept from anyone!?
Aber was ist mit dem UseCase: Ein Laptop, zweimal den Client gestartet. Da will man doch
unterschiedliche client_identification_ids haben, oder nicht? Also sollte der Server nen Deny
senden für die client_identification_id und der client ne neue id erzeugen (und
als zweite, dritte... id auch lokal im config file /shared/oder runtime Ordner ablegen)?

Vielleicht sollte das abhängig sein von dem connection-status von den der
client_identification_id assoziierten connections.
Just connected and everything is fine -> force new client_identification_id
Or only stale connections but client_identification_id is associated with a running game?
-> Allow reconnect.
Oder even interactive? Server sendet EntscheidungsAnfrage, client darf dann aussuchen ob
er der session joinen will oder eigene neue session haben möchte?


### Lobby

Depending on the state of the session associated with the `client_identification_id`, the
server shall now send a `WelcomeToLobbyMsg` or a `GamestateMsg` for a running game.

The client can now send `TxChatMsg`s (contains message) and should render received
`RxChatMsg`s (contains msg, name of user and timestamp).

The server should distribute each incoming `TxChatMsg`, according to its context (lobby,
a certain game, whisper to certain user), to the related connections using `RxChatMsg`s.

If the server logs the content of chat messages other than those in the Lobby, this shall
be clearly stated in a "Welcome"-`RxChatMsg` send to each new client connecting.


### Start a Game

To start a game, the client should send a `InitGameMsg`, `JoinGame`, `AutoJoinMsg`
or `AcceptInviteMsg` as a reply to a `InviteMsg` from the server.

As soon as a `InitGameMsg` was sent (or a `AutoJoinMsg` without any open `Game` to join), a new
`Game` is started. The `gamestate` of the new `Game` should be `open` or `invite_only`. When a
second player joined, it should change to `starting` and change to `running`
after both player agreed on the game parameter (size, which player is Player1, if to start
on an empty board or load a game from a saved game). When a game has ended (winner 1, 2 or draw),
the `gamestate` should be `finished`.


### Play a Game

While a game is running, the client should render incoming `GameStateMsg`s. The client may request
a recent game state with a `RequestGameStateMsg`. A `GameStateMsg` contains:
 * `gamestate`
 * gameboard size
 * who is Player1, who is Player2 - do not use `client_identification_id` in messages send to the clients...
   instead prepare the messages individualy for both clients and tell them "you are player x (1/2 or None for observer)"
 * filename of board to load (from server?!?) or datastructure with board to start with?!

When the `gamestate` is `running`:
 * a serializable version of the Gameboard object with its Boxes.
 * last_move, current player, wincounter, winner, ...
 * optional a game history

How to handle History? If sent by server, make it "scrollable", if not do not track it.

If it is the clients turn, the client should send a `MoveMsg`.

The server should answer with a new GameState or a `InvalidMoveErrorMsg`. The server may
also send TxChatMsgs to both players with details on the last move. If the server does so,
this there shall be a possibility, to disable this behaviour. There should be either a global
CLI parameter for the whole server to disable it or users should be able to use a
`DisableMoveChatMsg` to disable the feature in the current game or even as default for future games.


### Game ended
...


### Highscore
...


### Admin Authorization
...


### Store Sessions in SqLiteDB
The server may store all information about the current connections, sessions and games
in a local SqLite Database. This would allow seamless recovery on a server restart.



## Server

### CLI Parameter

```
  --listen IP (default to all interfaces)
  --port PORT (default 2345)
  --name NAME (default "Käsekästchen-Server")
  --max-connections...
```

A global Msg-In-Queue and Msg-Out-Queue for each connection shall be implemented.

All connection treads write received data to the single Msg-In-Queue and read from their
individual Msg-Out-Queue data that should be sent to the client.

The main thread of the server will take care of new connections. A separate server thread
handles the heavy load of reading the global Msg-In-Queue and writing appropriate objects
to the related individual Msg-Out-Queues.


## Client

### CLI Parameter

```
  --server IP (default to all interfaces)
  --port PORT (default 2345)
  --name NAME (default "Player RANDOM_NUMBER")
  --session-id STRING or INT indicating the number of the key in the list in the local config file
```

When a client detects a disconnect (or forced a disconnect due to a timeout on `KeepAliveAckMsg`s)
it may try to reconnect to the server. It should use a 10 seconds delay between two attempts.

maybe we can detect if another instance of the client is already running on the same system
and then automatically use a second client_identification_id?

or at least hve separate sections for pygame and tkinter in the local client config
file where a list of client_identification_ids is in the common part and in each subsection
there can be a different default which key to use first... ?



## Keepalive

All clients shall send a `KeepAliveMsg` every 5 seconds to the server.

The server shall reply with a `KeepAliveAckMsg` as soon as possible.

If the Server haven't received a `KeepAliveMsg` from a certain client
for more than 30 seconds, it should terminate that connection.
