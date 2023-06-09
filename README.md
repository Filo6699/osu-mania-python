# Unofficial osu!mania multiplayer lobby

**This project was made for learning purposes and based on a game called ![osu!](https://osu.ppy.sh/)** (mania game mode to be exact)

## Used libraries
+ PyGame
+ Internal libs
  + socket
  + threading
  + json

## Project features
- [ ] Networking
  - [x] Pockets
  - [x] Auth system
  - [ ] Database connection
- [ ] Scenes (thx to ![justlian](https://github.com/JustLian) for the idea)
  - [x] Scene manager
  - [x] Login & Register scenes
  - [ ] Lobby scene
  - [ ] Game scene
- [x] A lot of OOP
- [x] Mental issues 🎉

# How to use
## Installation
* `git clone https://github.com/Filo6699/chatroom`
* `cd chatroom`
* `python -m pip install -r requirements.txt`
### Create a config.json file in project's root folder
```
{
  "host": "host.ip.here.thx",
  "port": port (as number)
}
```

# Client
*You can't play without a server to connect to*

Run `python -m client` in project's root folder

# Server
*Servers are basicly a lobby. You can't host multiple lobbies on 1 server*

Run `python -m server` in project's root folder