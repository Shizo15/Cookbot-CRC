import asyncio
import discord
import discord.ext.commands as commands
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


async def main():
    await bot.load_extension("commands.recipe")
    await bot.load_extension("commands.meal")
    await bot.load_extension("commands.cuisine")
    await bot.load_extension("commands.random")
    await bot.load_extension("commands.ingredients")
    await bot.load_extension("commands.helpme")


API_KEY = os.getenv("API_KEY")

user_favorites = {}


@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name != "❤️":
        return

    channel = bot.get_channel(payload.channel_id)
    if not channel:
        return

    message = await channel.fetch_message(payload.message_id)

    if message.author.id != bot.user.id:
        return

    user_id = payload.user_id
    if user_id == bot.user.id:
        return

    favs = user_favorites.get(user_id, [])
    if payload.message_id not in favs:
        favs.append(payload.message_id)
        user_favorites[user_id] = favs

        print(f"✅ User {user_id} added recipe {payload.message_id} to favorites.")


@bot.event
async def on_raw_reaction_remove(payload):
    if payload.emoji.name != "❤️":
        return

    user_id = payload.user_id
    favs = user_favorites.get(user_id, [])

    if payload.message_id in favs:
        favs.remove(payload.message_id)
        user_favorites[user_id] = favs
        print(f"❌ User {user_id} deleted recipe {payload.message_id} from favorites.")


@bot.command(name="favorites")
async def favorites(ctx):
    favs = user_favorites.get(ctx.author.id, [])
    if not favs:
        await ctx.send("You don't have any favorite recipes yet.❤️")
        return

    message = "📌 Your favorite recipes:\n" + "\n".join(
        [
            f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{mid}"
            for mid in favs
        ]
    )
    await ctx.send(message)



if __name__ == "__main__":
    logging.info("Cookbot starting...")
    asyncio.run(main())
    bot.run(DISCORD_TOKEN)
