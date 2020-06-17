# Discord Teamspeak Status Bot

This is a small discord bot, that checks the status of a teamspeak server.

## Installation

Please clone the repository and navigate to the working directory and build the Docker container.

```bash
docker build -t dicord-teamspeak-status-bot .
```

After the operation you can start the bot, you need to change the variables as you need it.

```bash
docker run --detach -e "token=[Your Token]" -e "ts3_host=[Host]" -e "ts3_port=10011" -e "ts3_username=[Username]" -e "ts3_password=[Password]" --name dicord-bot-teamspeak-status dicord-teamspeak-status-bot
```

## Usage

In discord mention the bot name and type help to get a list with commands

Type "$temspeak" to get the status

Type "$teamspeak clients" to get a clientlist
