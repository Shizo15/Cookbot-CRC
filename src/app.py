import discord
import discord.ext.commands as commands
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

API_KEY = os.getenv("API_KEY")

async def random_recipe():
    response = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={API_KEY}")
    data = response.json()
    recipe = data["recipes"][0]

    title = recipe["title"]
    instructions = recipe.get("instructions", "Brak instrukcji 😢")
    image_url = recipe.get("image", "")

    embed = discord.Embed(
        title=title,
        description=instructions[:2048],  # Discord ma limit na opis
        color=discord.Color.green()
    )

    if image_url:
        embed.set_image(url=image_url)

    return embed


@client.event
async def on_ready():
    print(f'Zalogowano jako {client.user}')

@client.event
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!losowy'):
        recipe_embed = await random_recipe()
        await message.channel.send(embed=recipe_embed)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
client.run(f"{DISCORD_TOKEN}")
