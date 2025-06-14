![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.1-yellow.svg)
![Socket.IO](https://img.shields.io/badge/Socket.IO-4.7.5-black.svg?logo=socket.io)
![Redis](https://img.shields.io/badge/Redis-5.0.1-red.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.22-orange.svg)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2.2-3178C6.svg)
![Vite](https://img.shields.io/badge/Vite-5.2.0-646CFF.svg)
![Vite](https://img.shields.io/badge/PostgreSQL-17.5-purple.svg)


# Project color conquerer

Simple online turn based board game where you need to defeat the opponent by damaging their master cell with the help of your own minion cells.

![image](https://i.imgur.com/wUTYZCw.png)

This is a portfolio project and although deployed on the internet, it is not intended for commercial use.
Currently licensed under the Creative Commons Attribution-NonCommercial 4.0 license (see [LICENSE](./LICENSE)).

# Game rules

- 1v1 matches, turn based.
- Fixed 11 by 11 square grid, where cells are the individual grid squares that may be controlled by a player.
- A player wins when their opponent's health reaches 0.
- Master cells (deep blue and red cells) represent their respective player. Basically, the blue team is you and the red team is your opponent.
- A player loses HP whenever their master cell takes damage.
- Players begin with 1 mana point each and gain an additional one each turn, up to a maximum of 9.
- Mana points can be used to spawn cells or cast spells.
- Cells can move or attack each turn, except the turn where they were spawned.
- Starting from their second turn, players lose 1 stamina point per turn. Once they arrive at 0 stamina, they enter the fatigue state and start taking damage at the beginning of each turn.
- Fatigue damage gradually increases over the turns, incremented by 1 (first 1 damage, then 2, 3, etc.).
- Spells are special actions that players may use directly from their action bar.
- Spells allow the player to restore their stamina (1 spell casting = 1 stamina point restored).
- Each spell can only be cast a fixed number of times during the match.

### Additional information

- Inactivity warnings pop up after a certain amount of time when the player did not perform any action (such as spawning a cell, or ending their turn for example) and eventually lead to the player's automatic loss if they do not participate in the game.
- Players may concede the game to their opponent at any time.
- Currently, only English is supported.

# How to play

Go to the official website at [colorconquerer.com](https://colorconquerer.com).
Press the Play button and wait for an opponent.

Note: It is very unlikely that anyone is queuing so you may open up another browser or incognito tab to play against yourself.

![image](https://i.imgur.com/spMHIx4.png)

Once an opponent has been found, the match starts. Try to defeat your opponent. Good luck!