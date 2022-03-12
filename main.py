# a discord bot for registration in the server
# | IMPORT
import discord
import os

from dotenv import load_dotenv
from typing import Union

from utils.command import command_parse
from utils import log

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
load_dotenv()
CLIENT = discord.Client()
LOGGER = log.logger(log_dir="logs")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")
HELP_MSG=f"""

──────────────

ℹ️ **Description** ℹ️
──────────────
**A registration bot for discord**

_If you want to send a string with space inside (i.e., Test Name), You must enclose a string with `"` (i.e., "Test Name")_

⚙️ **Command** ⚙️
──────────────
**`{COMMAND_PREFIX}help`**
**__Description__**: Show this message.

**`{COMMAND_PREFIX}regis [server_name] [name]`**
**__Description__**: Initiate registration process.
**__Parameter__**:
        **`server_name`**: server name. 
        **`name`**: your name
"""

# | FUNCTIONS
async def get_channel_from_id(msg: discord.Message) -> discord.channel:
    global CLIENT

    if msg.guild is not None:
        ch = CLIENT.get_channel(msg.channel.id)
    else:
        ch = await msg.author.create_dm()

    return ch

def get_server_from_name(server_name: str) -> Union[discord.Guild, None]:
    global CLIENT

    for s in CLIENT.guilds:
        if s.name == server_name:
            return s
    return None

@CLIENT.event
async def on_ready() -> None:
    global LOGGER

    LOGGER.print_log("Ready!", log_level=log.INFO)

@CLIENT.event
async def on_message(msg: discord.Message) -> None:
    global CLIENT
    global HELP_MSG
    global LOGGER

    author = msg.author
    author_id = author.id
    client_id = CLIENT.user.id

    if author_id != client_id:
        ch = await get_channel_from_id(msg)
        async with ch.typing():
            parsed_cmd = command_parse(msg.content, COMMAND_PREFIX)
            if parsed_cmd is not None:
                cmd = parsed_cmd["command"]
                if cmd == "help":
                    LOGGER.print_log(f"{author} use {COMMAND_PREFIX+cmd} command", log.INFO)
                    help_msg = discord.Embed(
                            title="❓Help❓",
                            description=HELP_MSG,
                            color=discord.Color.random(),
                        )
                    await ch.send(embed=help_msg)
                elif msg.guild is None:
                    if cmd == "regis":
                        LOGGER.print_log(f"{author} use {COMMAND_PREFIX+cmd} command", log.INFO)
                        _server_name = parsed_cmd["param"]["server_name"]
                        _name = parsed_cmd["param"]["name"]
                        _server = get_server_from_name(_server_name)
                        print(_server)
                        if _server is None:
                            LOGGER.print_log(f"{_server_name} is used in {COMMAND_PREFIX+cmd} as a param but can not access", log.INFO)
                            await ch.send(f"I can't go to `{_server_name}`! 😣")
                            return
                        else:
                            await ch.send(f"got {_server_name} {_name}")
            else:
                LOGGER.print_log(f"{author} sent a unknown/incomplete command [{msg.content}]", log.INFO)
                await ch.send(f"I don't understand that! 🤨\nUse `{COMMAND_PREFIX}help` to get helping message.")


# | MAIN
if __name__ == "__main__":
    CLIENT.run(os.getenv("DISCORD_BOT_TOKEN"))
    # https://discord.com/api/oauth2/authorize?client_id=951658220844384288&permissions=1099780320368&scope=bot