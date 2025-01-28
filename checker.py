import discord
import requests
import asyncio

DISCORD_BOT_TOKEN = "your bots token"

USER_ID = "roblox user id"

CHANNEL_ID = "discord channel ID" # without quotation marks

USER_TO_PING = "discord user ID" # without quotation marks

PRESENCE_API = "https://presence.roblox.com/v1/presence/users"

previous_status = None
monitoring = True

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def fetch_player_status(user_id):
    try:
        response = requests.post(PRESENCE_API, json={"userIds": [user_id]})
        data = response.json()
        if "userPresences" in data:
            presence = data["userPresences"][0]
            return {
                "status": presence["userPresenceType"],
                "game_name": presence.get("lastLocation", ""),
            }
    except Exception as e:
        print(f"Error fetching player status: {e}")
    return None

async def monitor_status(channel):
    global previous_status, monitoring
    status_mapping = {0: "Offline", 1: "Online", 2: "In-Game"}
    user_mention = f"<@{USER_TO_PING}>"

    player_status = fetch_player_status(USER_ID)
    if player_status:
        current_status = player_status["status"]
        game_name = player_status["game_name"]
        status_text = status_mapping.get(current_status, "Unknown")
        initial_message = f"{user_mention}, Player's current status: {status_text}"
        if current_status == 2 and game_name:
            initial_message += f" in {game_name}"
        await channel.send(initial_message)
        previous_status = current_status

    while monitoring:
        player_status = fetch_player_status(USER_ID)
        if player_status:
            current_status = player_status["status"]
            game_name = player_status["game_name"]

            if current_status != previous_status:
                status_text = status_mapping.get(current_status, "Unknown")
                message = f"{user_mention}, Player status changed: {status_text}"
                if current_status == 2 and game_name:
                    message += f" in {game_name}"
                await channel.send(message)
                previous_status = current_status

        await asyncio.sleep(8)

async def periodic_status_update(channel):
    while True:
        await channel.send("bot is still running.")
        await asyncio.sleep(1800)  # will send a message so user know the bot is still running

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        print(f"Monitoring Roblox status in channel: {CHANNEL_ID}")
        # Start both the monitoring and periodic status update tasks
        asyncio.create_task(monitor_status(channel))
        asyncio.create_task(periodic_status_update(channel))
    else:
        print("Could not find the specified channel. Please check the CHANNEL_ID.")

client.run(DISCORD_BOT_TOKEN)