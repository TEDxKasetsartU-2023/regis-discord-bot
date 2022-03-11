# a discord bot for registration in the server
# | IMPORT
import discord
import os

from dotenv import load_dotenv

from utils import log

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
load_dotenv()
CLIENT = discord.Client()
LOGGER = log.logger(log_dir="logs")

# | FUNCTIONS
@CLIENT.event
async def on_ready():
    LOGGER.print_log("Ready!", log_level=log.INFO)

# | MAIN
if __name__ == "__main__":
    CLIENT.run(os.getenv("DISCORD_BOT_TOKEN"))
    # https://discord.com/api/oauth2/authorize?client_id=951658220844384288&permissions=1099780320368&scope=bot