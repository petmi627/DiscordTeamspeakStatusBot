import os, discord, ts3, sys, logging

version = "1.0.2"
developed_by = "KywoSkylake: https://github.com/petmi627"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TeamspeakStatusClient(discord.Client):

    async def on_ready(self):
        """
        The Bot started
        :return:
        """
        logger.info("I started up. Beep Bop")
        await self.change_presence(activity=discord.Game(name="mention me with a message containing the word help"))

    async def on_message(self, message):
        if message.author == client.user:
            return

        if client.user in message.mentions:
            self.logUserMessage(message)
            if "help" in message.content.lower():
                await message.channel.send('Type `$teamspeak` or `$ts3` to get the status of the Teamspeak Server\n'
                                       'Type `$teamspeak clients` or `$ts3 clients` to view the clients connected')
            if "version" in message.content.lower():
                await message.channel.send('The bot version is {}'.format(version))
            if "creator" in message.content.lower() or "master" in message.content.lower() \
                    or "developer" in message.content.lower() or "created" in message.content.lower():
                await message.channel.send('I was created by my master {}'.format(developed_by))

        if self.startsWith(message.content.lower(), ["$", "?", "!", "/"]):
            self.logUserMessage(message)
            message_received = message.content.lower()[1:]
            if self.startsWith(message_received, ['teamspeak', 'teamspeak3', 'ts3']):
                msg = await message.channel.send("Fetching data, please wait")
                try:
                    with ts3.query.TS3Connection(os.environ['ts3_host'], port=os.environ['ts3_port']) as ts3conn:
                        try:
                            ts3conn.login(
                                client_login_name=os.environ['ts3_username'],
                                client_login_password=os.environ['ts3_password']
                            )
                        except ts3.query.TS3QueryError as err:
                            logger.error("Login failed: {}".format(err.resp.error["msg"]), exc_info=True)
                            await message.channel.send(":x: Sorry I ran into an error")

                        ts3conn.use(sid=1)
                        if "clients" in message.content:
                            await message.channel.send(self.getClientlist(ts3conn))
                        else:
                            await message.channel.send(self.getServerStatus(ts3conn))
                        await msg.delete()
                except ts3.query.TS3QueryError as err:
                    logger.error("Login failed: {}".format(err.resp.error["msg"]), exc_info=True)
                    await msg.delete()
                    await message.channel.send(":x: Sorry I ran into an error")
                except ts3.query.TS3TimeoutError as err:
                    logger.error("Login failed: {}".format(err.resp.error["msg"]), exc_info=True)
                    await msg.delete()
                    await message.channel.send(":x: The teamspeak server seems to be offline")

    def getServerStatus(self, ts3conn):
        resp = ts3conn.serverinfo()
        logger.info("Fetching serverinformation from the Teamspeak Server")
        return ":white_check_mark: {} is currently online,\n{}/{} clients are currently connected.\nThe server is online since {}.".format(
                resp.parsed[0]['virtualserver_name'],
                str(int(resp.parsed[0]['virtualserver_clientsonline']) - 1),
                resp.parsed[0]['virtualserver_maxclients'],
                self.getDaysFromTimestamp(resp.parsed[0]['virtualserver_uptime']))

    def getClientlist(self, ts3conn):
        resp_clientlist = ts3conn.clientlist()
        resp_serverinfo = ts3conn.serverinfo()

        logger.info("Fetching serverinformation and clientlist from the Teamspeak Server")
        msg = "{}/{} clients are currently connected\n".format(
            str(int(resp_serverinfo.parsed[0]['virtualserver_clientsonline']) - 1),
            resp_serverinfo.parsed[0]['virtualserver_maxclients'])
        if len(resp_clientlist) > 0:
            msg += "```python\n"
        index = 1
        for client in resp_clientlist:
            if int(client["client_type"]) == 0:
                msg += "Nr. {} - \"{}\"\n".format(str(index), client["client_nickname"])
                index += 1
            if len(resp_clientlist) == index:
                msg += "```"

        return msg

    def getDaysFromTimestamp(self, seconds):
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60

        days = int(seconds) // seconds_in_day
        hours = (int(seconds) - (days * seconds_in_day)) // seconds_in_hour
        minutes = (int(seconds) - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute

        if days == 0 and hours == 0 and minutes == 0:
            return "now"
        elif days == 0 and hours == 0:
            return str(minutes) + " " + self.plural("minute", "minutes", minutes)
        elif days == 0:
            return str(hours) + " " + self.plural("hour", "hours", hours) + " and " + str(
                minutes) + " " + self.plural("minute", "minutes", minutes)
        else:
            return str(days) + " " + self.plural("day", "days", days) + ", " + str(
                hours) + " " + self.plural("hour", "hours", hours) + " and " + str(
                minutes) + " " + self.plural("minute", "minutes", minutes)

    def plural(self, singluar, plural, count):
        if count == 1:
            return singluar
        else:
            return plural

    def logUserMessage(self, message):
        logger.info(
            "Message from {} in {} contains {}".format(str(message.author), message.channel, message.content))

    def startsWith(self, message, list):
        for item in list:
            if str(message).startswith(item):
                return True
        return False

if '__main__' == __name__:
    client = TeamspeakStatusClient()
    client.run(os.environ['token'])