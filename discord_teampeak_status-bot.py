import os, discord, ts3, sys, logging

version = "1.0.0"
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
        logger.info("I started up. Beep Bop")

    async def on_message(self, message):
        if message.author == client.user:
            return

        if "help" in message.content and client.user in message.mentions:
            logger.info("Message from {} in {} contains {}".format(str(message.author), message.channel, message.content))
            await message.channel.send('Type "$teamspeak" to get the status of the Teamspeak Server\n'
                                       'Type "$teamspeak clients" to view the clients connected')
        if "version" in message.content and client.user in message.mentions:
            logger.info("Message from {} in {} contains {}".format(str(message.author), message.channel, message.content))
            await message.channel.send('The bot version is {}'.format(version))
        if ("creator" in message.content or "master" in message.content or "developer" in message.content) \
                and client.user in message.mentions:
            logger.info("Message from {} in {} contains {}".format(str(message.author), message.channel, message.content))
            await message.channel.send('I was created by {}'.format(developed_by))

        if "$teamspeak" in message.content:
            logger.info(
                "Message from {} in {} contains {}".format(str(message.author), message.channel, message.content))
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
                        await message.channel.send("Sorry I ran into an error")

                    ts3conn.use(sid=1)
                    if "clients" in message.content:
                        await message.channel.send(self.getClientlist(ts3conn))
                    else:
                        await message.channel.send(self.getServerStatus(ts3conn))

                    await msg.delete()

            except ts3.query.TS3QueryError:
                logger.error("Login failed: {}".format(err.resp.error["msg"]), exc_info=True)
                await message.channel.send("Sorry I ran into an error")
            except ts3.query.TS3TimeoutError:
                logger.error("Login failed: {}".format(err.resp.error["msg"]), exc_info=True)
                await message.channel.send("The teamspeak server seems to be offline")

    def getServerStatus(self, ts3conn):
        resp = ts3conn.serverinfo()
        logger.info("Fetching serverinformation from the Teamspeak Server")
        return "{} is currently online,\n{}/{} clients are currently connected.\nThe server is online since {}.".format(
                resp.parsed[0]['virtualserver_name'],
                str(int(resp.parsed[0]['virtualserver_clientsonline']) - 1),
                resp.parsed[0]['virtualserver_maxclients'],
                self.getDaysFromTimestamp(resp.parsed[0]['virtualserver_uptime']))

    def getClientlist(self, ts3conn):
        resp_clientlist = ts3conn.clientlist()
        resp_serverinfo = ts3conn.serverinfo()

        logger.info("Fetching serverinformation and clientlist from the Teamspeak Server")
        msg = "{}/{} clients are currently connected\n\n".format(
            str(int(resp_serverinfo.parsed[0]['virtualserver_clientsonline']) - 1),
            resp_serverinfo.parsed[0]['virtualserver_maxclients'])
        msg += "Here is the client list\n"
        index = 1
        for client in resp_clientlist:
            if int(client["client_type"]) == 0:
                msg += "#{} - {}\n".format(str(index), client["client_nickname"])
                index += 1

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
            return str(minutes) + " " + self.plurify("minute", "minutes", minutes)
        elif days == 0:
            return str(hours) + " " + self.plurify("hour", "hours", hours) + " and " + str(
                minutes) + " " + self.plurify("minute", "minutes", minutes)
        else:
            return str(days) + " " + self.plurify("day", "days", days) + ", " + str(
                hours) + " " + self.plurify("hour", "hours", hours) + " and " + str(
                minutes) + " " + self.plurify("minute", "minutes", minutes)

    def plurify(self, singluar, plural, count):
        if count == 1:
            return singluar
        else:
            return plural

if '__main__' == __name__:
    client = TeamspeakStatusClient()
    client.run(os.environ['token'])