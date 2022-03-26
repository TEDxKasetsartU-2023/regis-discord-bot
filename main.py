# a discord bot for registration in the server
# | IMPORT
import discord
import os

from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Union

from googleModule.main import gmail_management, init_creds, sheet_management
from googleModule.parseSheet import parseSheet
from utils import log
from utils.command import command_parse
from utils.OTP import gen_otp, read_otp_file, write_otp_file

# | GLOBAL EXECUTIONS & GLOBAL VARIABLES
load_dotenv()
OTP_FILE = os.getenv("OTP_FILE")
SENDER_MAIL = os.getenv("SENDER_MAIL")
CLIENT = discord.Client(intents=discord.Intents.all())
LOGGER = log.logger(log_dir="logs")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX")
HELP_MSG = f"""

──────────────

ℹ️ **รายะเอียด** ℹ️
──────────────
**น้องแมวลงทะเบียนเข้าเซิฟเวอร์ของดิสคอร์ด**

_ถ้าอยากจะส่งข้อความที่มีวรรคอยู่ (เช่น Test Name), ต้องใช้เครื่องหมายคำพูด `"` (เช่น "Test Name")_

⚙️ **คำสั่ง** ⚙️
──────────────
**`{COMMAND_PREFIX}help`**
**__Description__**: ขอความช่วยเหลือให้น้องบอกวิธีใช้งานตัวเอง

**`{COMMAND_PREFIX}regis [ชื่อเซิฟเวอร์] [ชื่อ]`**
**__Description__**: เริ่มต้นการลงทะเบียนกับน้องทองหยอด
**__Parameter__**:
        **`server_name`**: ชื่อของเซิฟเวอร์ที่ต้องการลงทะเบียน 
        **`name`**: ชื่อของคุณที่ต้องใช้ในการลงทะเบียน

**`{COMMAND_PREFIX}otp [OTP]`**
**__Description__**: ยืนยันตัวตนกับน้องทองหยอดด้วย OTP
**__Parameter__**:
        **`OTP`**: One-Time Password ที่ส่งไปทางอีเมล
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


async def set_role(author: discord.User, server_name: str, raw_role: str):
    _server = get_server_from_name(server_name)
    for m in _server.members:
        if m.id == author.id:
            _member = m
    role_input = [r for r in raw_role.strip().split(",") if r != ""]
    for r in _server.roles:
        if r.name in role_input:
            await _member.add_roles(r)


@CLIENT.event
async def on_connect() -> None:
    global LOGGER

    LOGGER.print_log("Connected!", log_level=log.INFO)

@CLIENT.event
async def on_ready() -> None:
    global LOGGER

    LOGGER.print_log("Ready!", log_level=log.INFO)


@CLIENT.event
async def on_message(msg: discord.Message) -> None:
    global CLIENT
    global GMAIL
    global HELP_MSG
    global LOGGER
    global OTP_FILE
    global OTP_WAIT_LST
    global SENDER_MAIL
    global SHEET

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
                    LOGGER.print_log(
                        f"{author} use {COMMAND_PREFIX+cmd} command", log.INFO
                    )
                    help_msg = discord.Embed(
                        title="❓วิธีให้น้องทองหยอดช่วย❓",
                        description=HELP_MSG,
                        color=discord.Color.random(),
                    )
                    await ch.send(embed=help_msg)
                elif msg.guild is None:
                    if cmd == "regis":
                        LOGGER.print_log(
                            f"{author} use {COMMAND_PREFIX+cmd} command", log.INFO
                        )
                        _server_name = parsed_cmd["param"]["server_name"]
                        _name = parsed_cmd["param"]["name"]
                        _server = get_server_from_name(_server_name)
                        # print(_server)
                        if _server is None:
                            LOGGER.print_log(
                                f"{_server_name} is used in {COMMAND_PREFIX+cmd} as a param but can not access",
                                log.INFO,
                            )
                            await ch.send(f"I can't go to `{_server_name}`! 🙀")
                            return
                        else:
                            sheet_data = parseSheet(
                                SHEET.read_sheet_by_range(f"{_server_name}!A:D")[
                                    "values"
                                ]
                            )
                            user_data = None
                            user_row = -1
                            for line in range(len(sheet_data)):
                                if sheet_data[line]["ชื่อ"] == _name:
                                    user_data = sheet_data[line]
                                    user_row = line + 2
                                    break

                            if user_data is None:
                                LOGGER.print_log(
                                    f"{author} try to use regis command but not in the sheet",
                                    log.INFO,
                                )
                                await ch.send(
                                    f"Well... Who're you exactly? I don't think I know you! 😾"
                                )
                                return
                            elif user_data["สถานะ"] == "รอส่ง OTP":
                                await ch.send(
                                    f"Nope! I'm still waiting for your OTP. 😿"
                                )
                                return
                            elif user_data["สถานะ"] == "เสร็จสิ้นการลงทะเบียน":
                                await ch.send(f"Why do you want to register again? 😸")
                                return
                            elif user_data["สถานะ"] == "ยังไม่ได้ลงทะเบียน":
                                otp, ref = gen_otp(
                                    OTP_FILE, str(author), _server_name, 6
                                )
                                SHEET.write_sheet_by_range(
                                    f"D{user_row}", [["รอส่ง OTP"]]
                                )
                                OTP_WAIT_LST.append({author: [user_data, user_row]})
                                LOGGER.print_log(
                                    f"gmail response: {GMAIL.send_mail(to=user_data['อีเมล'], subject='TEDxKasetsartU Discord Server Registration OTP', otp=otp, ref=ref)}",
                                    log.INFO,
                                )
                                await ch.send(
                                    f"Go check your email! 📨 I've sent you an OTP with the ref. code `{ref}`. 🐱"
                                )
                                return
                    elif cmd == "otp":
                        _otp = parsed_cmd["param"]["otp"]
                        wait_data = None
                        for d in OTP_WAIT_LST:
                            if author in d.keys():
                                wait_data = d
                                break

                        if wait_data is not None:
                            data = read_otp_file(OTP_FILE)
                            try:
                                otp_data = data[_otp]
                            except KeyError:
                                LOGGER.print_log(
                                    f"{author} has sent an invalid OTP", log.INFO
                                )
                                await ch.send(
                                    f"That is not my OTP! Where do you get that from? 😾\nMake sure that you get the correct OTP by checking the ref. code! 😺"
                                )
                                return
                            old_wait_data = wait_data
                            user_row = wait_data[author][1]
                            sheet_data = parseSheet(
                                SHEET.read_sheet_by_range(f"{otp_data['server']}!A:D")[
                                    "values"
                                ]
                            )
                            user_data = None
                            for line in range(len(sheet_data)):
                                if line == user_row - 2:
                                    user_data = sheet_data[line]
                                    break
                            wait_data = {author: [user_data, user_row]}

                            if str(author) == otp_data["for"]:
                                if datetime.now() - otp_data["create_at"] <= timedelta(
                                    minutes=5
                                ):
                                    OTP_WAIT_LST.remove(old_wait_data)
                                    write_otp_file(
                                        OTP_FILE, _otp, "", "", "", mode="remove"
                                    )
                                    SHEET.write_sheet_by_range(
                                        f"D{wait_data[author][1]}",
                                        [["เสร็จสิ้นการลงทะเบียน"]],
                                    )
                                    await set_role(
                                        author,
                                        otp_data["server"],
                                        wait_data[author][0]["ฝ่าย"],
                                    )
                                    await ch.send(f"It's done! Congratulations 😸🎉")
                                    return
                                else:
                                    OTP_WAIT_LST.remove(old_wait_data)
                                    write_otp_file(
                                        OTP_FILE, _otp, "", "", "", mode="remove"
                                    )
                                    SHEET.write_sheet_by_range(
                                        f"D{wait_data[author][1]}",
                                        [["ยังไม่ได้ลงทะเบียน"]],
                                    )
                                    LOGGER.print_log(
                                        f"{author} has sent an expire OTP", log.INFO
                                    )
                                    await ch.send(
                                        f"Well... You took too long! My little OTP has been expire. 🙀\nGo back to `$regis` again!"
                                    )
                                    return
                            else:
                                LOGGER.print_log(
                                    f"{author} has sent the other OTP", log.INFO
                                )
                                await ch.send(
                                    f"That is not your OTP! Where do you get that from? 😾\nMake sure that you get the correct OTP by checking the ref. code! 😺"
                                )
                                return
                        else:
                            LOGGER.print_log(
                                f"{author} try to use otp before regis", log.INFO
                            )
                            await ch.send(
                                f"I do not expect you to send an OTP! Why do you send me that? 😾"
                            )
                            return
            else:
                LOGGER.print_log(
                    f"{author} sent a unknown/incomplete command [{msg.content}]",
                    log.INFO,
                )
                await ch.send(
                    f"I don't understand that! 🙀\nUse `{COMMAND_PREFIX}help` to get helping message."
                )


# | MAIN
if __name__ == "__main__":
    GMAIL_CREDS, SHEET_CREDS = init_creds(
        os.path.join("googleModule", "credentials.json"),
        os.path.join("googleModule", "key.json")
    )
    GMAIL = gmail_management(creds=GMAIL_CREDS)
    SHEET = sheet_management(
        sheet_id="1oxoO8yNdXKibjf3KFy-Iqwd4ON_O9Y8AUV42_KEVky4", creds=SHEET_CREDS
    )
    OTP_WAIT_LST = []
    CLIENT.run(os.getenv("DISCORD_BOT_TOKEN"))
    # https://discord.com/api/oauth2/authorize?client_id=951658220844384288&permissions=1099780320368&scope=bot
