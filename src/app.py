import discord
import discord.ext.commands as commands
import os
import requests
import json
from dotenv import load_dotenv
from HTMLCleaner import *
import logging
import random

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

API_KEY = os.getenv("API_KEY")

async def sender(ctx, *args, **kwargs):
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            logging.warning(
                f"No permission to send messages on this channel {ctx.channel} (ID: {ctx.channel.id})."
            )
            return None

    try:
        message = await ctx.send(*args, **kwargs)
        return message
    except discord.Forbidden:
        logging.warning(
            f"No permission to send messages on this channel {ctx.channel} (ID: {ctx.channel.id})."
        )
        return None

@bot.command(name="recipe")
async def recipe_by_name(ctx, *, dish_name:str):
    url = "https://api.spoonacular.com/recipes/complexSearch"

    first_params = {
        "query": dish_name,
        "number": 1,
        "apiKey": API_KEY
    }
    first_response = requests.get(url, params=first_params)
    first_data = first_response.json()
    first_results = first_data["results"]
    total_results = first_data.get("totalResults", 0)
    rand_result = random.randint(0, total_results-1)

    print("Matching results: ",rand_result+1)

    if not first_results:
        await ctx.send(f"Cannot find recipe for: **{dish_name}**")
        return
    # else:
    #     await ctx.send("We got smth")
    params = {
        "query": dish_name,
        "offset": rand_result,
        "number": 1,
        "addRecipeInformation": True,
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        await ctx.send("Failed to get recipe 😕")
        return

    data = response.json()
    results = data.get("results")

    recipe = results[0]
    title = recipe.get("title", "Unknown recipe")
    image_url = recipe.get("image", "")
    source = recipe.get("sourceUrl", "")

    embed = discord.Embed(
        title=title,
        url=source,
        colour=discord.Colour.blurple()
    )

    if image_url:
        embed.set_image(url=image_url)

    logging.info(f"Command '!recipe' was called with argument: {dish_name}.")

    await sender(ctx, embed=embed)


@bot.command(name="random")
async def random_recipe(ctx):
    response = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={API_KEY}")
    data = response.json()
    recipe = data["recipes"][0]

    title = recipe["title"]
    instructions_raw = recipe.get("instructions", "No instructions 😢")
    image_url = recipe.get("image", "")
    source_url = recipe.get("sourceUrl", "")

    cleaner = HTMLCleaner()
    instructions = cleaner.clean(instructions_raw)

    if len(instructions) > 1024:
        instructions = instructions[:1020] + "..."

    embed = discord.Embed(
        title=title,
        url=source_url,
        color=discord.Color.green()
    )
    #Dodać dane o:
    # servings,
    # readyInMinutes,
    # cookingMinutes
    # cuisines
    # dishTypes
    # summary?

    embed.add_field(name="Instructions", value=instructions, inline=False)

    if image_url:
        embed.set_image(url=image_url)

    logging.info("Command '!random' was called.")

    await sender(ctx, embed=embed)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(f"{DISCORD_TOKEN}")
