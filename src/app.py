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

user_favorites={}

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
    #Tu trzeba będzie wyświetlać:
    # składniki
    # porcje
    if image_url:
        embed.set_image(url=image_url)

    logging.info(f"Command '!recipe' was called with argument: {dish_name}.")

    #await sender(ctx, embed=embed)

    msg = await sender(ctx, embed=embed)
    if msg:
        await msg.add_reaction("❤️")


@bot.command(name="random")
async def random_recipe(ctx):
    response = requests.get(f"https://api.spoonacular.com/recipes/random?apiKey={API_KEY}")
    data = response.json()
    recipe = data["recipes"][0]

    title = recipe["title"]
    instructions_raw = recipe.get("instructions", "No instructions 😢")
    image_url = recipe.get("image", "")
    source_url = recipe.get("sourceUrl", "")
    summary= recipe.get("summary", "")
    servings = recipe.get("servings", 0)
    ready_in_minutes = recipe.get("readyInMinutes", 0)
    cuisines = recipe.get("cuisines", 0)
    dish_types = recipe.get("dishTypes", "")
    price = recipe.get("pricePerServing", 0)
    diets = recipe.get("diets", 0)

    cleaner = HTMLCleaner()
    instructions = cleaner.clean(instructions_raw)

    if len(instructions) > 1024:
        instructions = instructions[:1020] + "..."

    embed = discord.Embed(
        title=title,
        url=source_url,
        color=discord.Color.green()
    )

    formatted_cuisine="\n".join(f"• {item}" for item in cuisines)
    formatted_dish_types="\n".join(f"• {item}" for item in dish_types)
    formatted_diets="\n".join(f"• {item}" for item in diets)
    price_in_usd=price/100

    embed.add_field(name="🍽️ Servings",value=servings,inline=True)
    embed.add_field(name="⏱️ Ready in",value=f"{ready_in_minutes} minutes",inline=True)
    embed.add_field(name="💰 Price Per Serving",value=f"{price_in_usd:.2f} USD",inline=True)
    if len(dish_types) > 0:
        embed.add_field(name="🍱 Dish type", value=formatted_dish_types, inline=True)

    if len(cuisines) > 0:
        embed.add_field(name="🌍 Cuisine",value=formatted_cuisine,inline=True)

    if len(diets) > 0:
        embed.add_field(name="🥗 Diet",value=formatted_diets,inline=True)
    #embed.add_field(name="Instructions", value=instructions,inline=False)

    if image_url:
        embed.set_image(url=image_url)

    logging.info("Command '!random' was called.")

    #await sender(ctx, embed=embed)

    msg = await sender(ctx, embed=embed)
    if msg:
        await msg.add_reaction("❤️")


#Dodać funckje szukania po składnikach

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
        await ctx.send("You don't have any favorites yet.❤️")
        return

    message = "📌 Your favorite recipes:\n" + "\n".join(
        [f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{mid}" for mid in favs])
    await ctx.send(message)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(f"{DISCORD_TOKEN}")
