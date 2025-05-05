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
async def recipe_by_name(ctx, *, args:str):
    #zobaczyć dlaczego się błędy robią jak nie poda się w query liczby przepisów
    #albo wywalić całkowicie ta liczbe przepisów do wyświetlenia
    parts = args.rsplit(" ", 1)
    try:
        number = int(parts[1])
        dish_name = parts[0]
    except IndexError:
        number = 1
        dish_name = parts[0]

    url = "https://api.spoonacular.com/recipes/complexSearch"

    first_params = {
        "query": dish_name,
        "number": number,
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

    params = {
        "query": dish_name,
        "offset": rand_result,
        "number": number,
        "addRecipeInformation": True,
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        await ctx.send("Failed to get recipe 😕")


    data = response.json()
    results = data.get("results")

    for recipe in results:
        title = recipe.get("title", "Unknown recipe")
        image_url = recipe.get("image", "")
        source = recipe.get("sourceUrl", "")
        recipe_id = recipe.get("id")

        embed = discord.Embed(
            title=title,
            url=source,
            colour=discord.Colour.blurple()
        )
        #Tu trzeba będzie wyświetlać:
        # porcje
        if image_url:
            embed.set_image(url=image_url)

        #2 request
        instructions_info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

        instructions_params={
            "apiKey": API_KEY,

        }
        instructions_response = requests.get(instructions_info_url, params=instructions_params)
        second_result = instructions_response.json()
        instructions_raw = second_result.get("instructions", "")

        #dodać do cleanera robienie instrukcji w punktach i żeby po kropce zaczynał nowy punkt
        cleaner = HTMLCleaner()
        instructions = cleaner.clean(instructions_raw)

        servings = second_result.get("servings", 0)
        #poprawić to na ogólny czas przygotowania bo nie podają w przepisach podzielonego na gotowanie itd.
        cooking_time = second_result.get("cookingMinutes", 0)
        preparation_time = second_result.get("preparationMinutes", 0)

        embed.add_field(name="🍽️ Servings", value=servings, inline=True)
        embed.add_field(name="⏱️ Preparation time", value=preparation_time, inline=True)
        embed.add_field(name="⏱️ Cooking time", value=cooking_time, inline=True)

        ingredients = second_result.get("extendedIngredients", [])

        ingredient_list = []
        for item in ingredients:
            name = item.get("name", "unknown")
            amount = item.get("amount", 0)
            unit = item.get("unit", "")
            ingredient_list.append(f"• {amount} {unit} {name}".strip())

        formatted_ingredients = "\n".join(ingredient_list)

        msg = await sender(ctx, embed=embed)
        if msg:
            await msg.add_reaction("❤️")
        await ctx.send(f"📋 **Ingredients:**\n{formatted_ingredients}\n")
        await ctx.send(f"\n📖 **Instructions for {title}:**\n{instructions}")

    logging.info(f"Command '!recipe' was called with argument: {dish_name}.")

# dodać jeszcze szukanie losowych na konkretną porę dnia albo określona kuchnia (include tags),
# chyba będzie lepiej to zrobić przez recipe a nie random bo jest więcej możliwości wyszukiwania

@bot.command(name="ingredients")
async def search_by_ingredients(ctx, *, ingredients:str):
    parts = ingredients.rsplit(" ", 1)
    try:
        number=int(parts[1])
        ingredients = parts[0]
    except IndexError:
        number=1
        ingredients=ingredients

    url = "https://api.spoonacular.com/recipes/findByIngredients"

    params = {
        "ingredients": ingredients,
        "number": number,
        "ranking":2,
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        await ctx.send("Failed to get recipes 😕")
        return

    data = response.json()

    if not data:
        await ctx.send("No recipes found")
        return

    for recipe in data:
        title = recipe["title"]
        image_url = recipe["image"]
        missed_ingredients = ", ".join([i["name"] for i in recipe.get("missedIngredients", [])])
        recipe_id=recipe["id"]

        #2 request
        info_url=f"https://api.spoonacular.com/recipes/{recipe_id}/information"

        info_params = {
            "apiKey": API_KEY
        }
        info_response = requests.get(info_url, params=info_params)

        if info_response.status_code != 200:
            continue

        info = info_response.json()

        source_url = info.get("sourceUrl", "")
        servings = info.get("servings", 0)
        ready_in = info.get("readyInMinutes",0)

        embed = discord.Embed(
            title=title,
            url=source_url,
            colour=discord.Colour.blurple()
        )
        embed.add_field(name="🛒 Missed Ingredients", value=missed_ingredients, inline=False)
        embed.add_field(name="🍽️ Servings", value=servings, inline=True)
        embed.add_field(name="⏱️ Ready In", value=ready_in, inline=True)
        embed.set_image(url=image_url)

        msg = await sender(ctx, embed=embed)
        if msg:
            await msg.add_reaction("❤️")

    logging.info(f"Command '!ingredients' was called with argument: {ingredients}.")

#Tu trzeba jeszcze zrobić coś aby te przepisy losowo się szukały, bo jak wyśweitlamy po 1 to ciąglem pokazuje ten sam przepis

@bot.command(name="random")
async def random_recipe(ctx, number:int=1):
    url = "https://api.spoonacular.com/recipes/random"

    params = {
        "number": number,
        "apiKey": API_KEY,
    }

    #Dać limit na ilośc zapytań w jednym poleceniu np. max 5

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return

    data = response.json()
    recipes = data["recipes"]

    for recipe in recipes:
        title = recipe["title"]
        instructions_raw = recipe.get("instructions", "No instructions 😢")
        image_url = recipe.get("image", "")
        source_url = recipe.get("sourceUrl", "")
        servings = recipe.get("servings", 0)
        ready_in_minutes = recipe.get("readyInMinutes", 0)
        cuisines = recipe.get("cuisines", 0)
        dish_types = recipe.get("dishTypes", "")
        price = recipe.get("pricePerServing", 0)
        diets = recipe.get("diets", 0)

        ###do wywalenia raczej
        cleaner = HTMLCleaner()
        instructions = cleaner.clean(instructions_raw)

        if len(instructions) > 1024:
            instructions = instructions[:1020] + "..."
        ###
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


        msg = await sender(ctx, embed=embed)
        if msg:
            await msg.add_reaction("❤️")

    logging.info("Command '!random' was called.")


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
        [f"https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{mid}" for mid in favs])
    await ctx.send(message)

@bot.command(name="helpme")
async def help_command(ctx):
    embed = discord.Embed(
        title="🍳 Help — Available Commands",
        description="Here's a list of commands you can use with this recipe bot:",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="`!recipe <name> [number]`",
        value="🔍 Searches for a recipe by name and shows a random matching result.\nExample: `!recipe pasta`",
        inline=False
    )

    embed.add_field(
        name="`!random`",
        value="🎲 Shows a completely random recipe.",
        inline=False
    )

    embed.add_field(
        name="`!favorites`",
        value="❤️ Displays your list of favorite recipes that you’ve added using the heart reaction.",
        inline=False
    )

    embed.add_field(
        name="`❤️ Reaction`",
        value="🫶 Add or remove a recipe from your favorites by clicking the heart emoji under a recipe message.",
        inline=False
    )

    embed.set_footer(text="Bon appétit! Made with Spoonacular API 🍽️")

    await ctx.send(embed=embed)


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(f"{DISCORD_TOKEN}")
