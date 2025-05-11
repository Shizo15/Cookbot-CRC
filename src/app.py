import discord
import discord.ext.commands as commands
import os
import requests
import json
from dotenv import load_dotenv
from HTMLCleaner import *
import logging
import random
from isHTML import *

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

    if not first_results:
        await ctx.send(f"Cannot find recipe for: **{dish_name}**")
        return

    if total_results > 1:
        await ctx.send(f"🔎 Matching results: **{total_results}**")

    rand_result = random.randint(0, total_results-1)

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


    data = response.json()
    results = data.get("results")

    for recipe in results:
        title = recipe.get("title", "Unknown recipe")
        image_url = recipe.get("image", "")
        source = recipe.get("sourceUrl", "")
        recipe_id = recipe.get("id", 0)

        embed = discord.Embed(
            title=title,
            url=source,
            colour=discord.Colour.blurple()
        )

        if image_url:
            embed.set_image(url=image_url)

        #2nd request
        instructions_info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

        instructions_params={
            "apiKey": API_KEY,
        }
        instructions_response = requests.get(instructions_info_url, params=instructions_params)
        second_result = instructions_response.json()

        instructions_raw = second_result.get("instructions", "")
        analyzed_instructions=second_result.get("analyzedInstructions", [])
        instructions=""

        if instructions_raw and is_html(instructions_raw):
            cleaner = HTMLCleaner()
            instructions = cleaner.clean(instructions_raw)

        if analyzed_instructions:
            steps=[]
            for step in analyzed_instructions[0].get("steps", []):
                steps.append(f"{step['number']}. {step['step']}")
            instructions = "\n".join(steps)

        if not instructions:
            instructions = "No instructions available 😢"


        servings = second_result.get("servings", 0)
        ready_in = second_result.get("readyInMinutes", 0)
        cuisines = recipe.get("cuisines", [])
        dish_types = recipe.get("dishTypes", [])
        price = recipe.get("pricePerServing", 0)
        diets = recipe.get("diets", [])
        source_name = recipe.get("sourceName", "")

        embed.add_field(name="🍽️ Servings", value=servings, inline=True)
        embed.add_field(name="⏱️ Ready in",value=f"{ready_in} minutes",inline=True)
        embed.add_field(name="💰 Price Per Serving", value=f"{price / 100:.2f} USD", inline=True)
        if dish_types:
            formatted_dish_types = "\n".join(f"• {item}" for item in dish_types)
            embed.add_field(name="🍱 Dish type", value=formatted_dish_types, inline=True)

        if cuisines:
            formatted_cuisine = "\n".join(f"• {item}" for item in cuisines)
            embed.add_field(name="🌍 Cuisine", value=formatted_cuisine, inline=True)

        if diets:
            formatted_diets = "\n".join(f"• {item}" for item in diets)
            embed.add_field(name="🥗 Diet", value=formatted_diets, inline=True)

        embed.set_footer(text=f"Source name: {source_name}")

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

##todo
## zmienić waluty kosztów posiłku?
## poprawić kod - wywalić duplikaty, ogarnąc nazwy
## podzielić funkcje na oddzielne pliki

@bot.command(name="meal")
async def search_by_type(ctx, *, recipe_type:str):
    parts = recipe_type.rsplit(" ", 1)
    try:
        number = int(parts[1])
        if number < 1 or number > 5:
            await ctx.send("❗ Please request between 1 and 5 recipes.")
            return

        dish_type = parts[0]
    except IndexError:
        number = 1
        dish_type = recipe_type

    url = "https://api.spoonacular.com/recipes/complexSearch"

    first_params = {
        "apiKey": API_KEY,
        "type": dish_type,
        "number": 1,
    }
    response = requests.get(url, params=first_params)

    if response.status_code != 200:
        await ctx.send("Failed to get recipes 😕")
        return

    first_response = requests.get(url, params=first_params)
    first_data = first_response.json()
    first_results = first_data["results"]
    total_results = first_data.get("totalResults", 0)

    if not first_results:
        await ctx.send(f"Cannot find recipes for: **{recipe_type}**")
        return

    if total_results > 1:
        await ctx.send(f"🔎 Matching results: **{total_results}**")

    rand_result = random.randint(0, total_results - 1)

    params = {
        "type":dish_type,
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
        recipe_id = recipe.get("id", 0)

        embed = discord.Embed(
            title=title,
            url=source,
            colour=discord.Colour.blurple()
        )

        if image_url:
            embed.set_image(url=image_url)

        # 2nd request
        instructions_info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

        instructions_params = {
            "apiKey": API_KEY,
        }
        instructions_response = requests.get(instructions_info_url, params=instructions_params)
        second_result = instructions_response.json()

        instructions_raw = second_result.get("instructions", "")
        analyzed_instructions = second_result.get("analyzedInstructions", [])
        instructions = ""

        if instructions_raw and is_html(instructions_raw):
            cleaner = HTMLCleaner()
            instructions = cleaner.clean(instructions_raw)

        if analyzed_instructions:
            steps = []
            for step in analyzed_instructions[0].get("steps", []):
                steps.append(f"{step['number']}. {step['step']}")
            instructions = "\n".join(steps)

        if not instructions:
            instructions = "No instructions available 😢"

        servings = second_result.get("servings", 0)
        ready_in = second_result.get("readyInMinutes", 0)
        cuisines = recipe.get("cuisines", [])
        dish_types = recipe.get("dishTypes", [])
        price = recipe.get("pricePerServing", 0)
        diets = recipe.get("diets", [])
        source_name = recipe.get("sourceName", "")

        embed.add_field(name="🍽️ Servings", value=servings, inline=True)
        embed.add_field(name="⏱️ Ready in", value=f"{ready_in} minutes", inline=True)
        embed.add_field(name="💰 Price Per Serving", value=f"{price / 100:.2f} USD", inline=True)
        if dish_types:
            formatted_dish_types = "\n".join(f"• {item}" for item in dish_types)
            embed.add_field(name="🍱 Dish type", value=formatted_dish_types, inline=True)

        if cuisines:
            formatted_cuisine = "\n".join(f"• {item}" for item in cuisines)
            embed.add_field(name="🌍 Cuisine", value=formatted_cuisine, inline=True)

        if diets:
            formatted_diets = "\n".join(f"• {item}" for item in diets)
            embed.add_field(name="🥗 Diet", value=formatted_diets, inline=True)

        embed.set_footer(text=f"Source name: {source_name}")

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

    logging.info(f"Command '!cuisine' was called with argument: {dish_type}.")

@bot.command(name="cuisine")
async def search_by_cuisine(ctx, *, cuisine:str):
    parts = cuisine.rsplit(" ", 1)
    try:
        number = int(parts[1])
        if number < 1 or number > 5:
            await ctx.send("❗ Please request between 1 and 5 recipes.")
            return

        cuisine_type = parts[0]
    except IndexError:
        number = 1
        cuisine_type = cuisine

    url = "https://api.spoonacular.com/recipes/complexSearch"

    first_params = {
        "apiKey": API_KEY,
        "cuisine": cuisine_type,
        "number": 1,
    }
    response = requests.get(url, params=first_params)

    if response.status_code != 200:
        await ctx.send("Failed to get recipes 😕")
        return

    first_response = requests.get(url, params=first_params)
    first_data = first_response.json()
    first_results = first_data["results"]
    total_results = first_data.get("totalResults", 0)

    if not first_results:
        await ctx.send(f"Cannot find recipes for: **{cuisine}**")
        return

    if total_results > 1:
        await ctx.send(f"🔎 Matching results: **{total_results}**")

    rand_result = random.randint(0, total_results - 1)

    params = {
        "type": cuisine_type,
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
        recipe_id = recipe.get("id", 0)

        embed = discord.Embed(
            title=title,
            url=source,
            colour=discord.Colour.blurple()
        )

        if image_url:
            embed.set_image(url=image_url)

        # 2nd request
        instructions_info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

        instructions_params = {
            "apiKey": API_KEY,
        }
        instructions_response = requests.get(instructions_info_url, params=instructions_params)
        second_result = instructions_response.json()

        instructions_raw = second_result.get("instructions", "")
        analyzed_instructions = second_result.get("analyzedInstructions", [])
        instructions = ""

        if instructions_raw and is_html(instructions_raw):
            cleaner = HTMLCleaner()
            instructions = cleaner.clean(instructions_raw)

        if analyzed_instructions:
            steps = []
            for step in analyzed_instructions[0].get("steps", []):
                steps.append(f"{step['number']}. {step['step']}")
            instructions = "\n".join(steps)

        if not instructions:
            instructions = "No instructions available 😢"

        servings = second_result.get("servings", 0)
        ready_in = second_result.get("readyInMinutes", 0)
        cuisines = recipe.get("cuisines", [])
        dish_types = recipe.get("dishTypes", [])
        price = recipe.get("pricePerServing", 0)
        diets = recipe.get("diets", [])
        source_name = recipe.get("sourceName", "")

        embed.add_field(name="🍽️ Servings", value=servings, inline=True)
        embed.add_field(name="⏱️ Ready in", value=f"{ready_in} minutes", inline=True)
        embed.add_field(name="💰 Price Per Serving", value=f"{price / 100:.2f} USD", inline=True)
        if dish_types:
            formatted_dish_types = "\n".join(f"• {item}" for item in dish_types)
            embed.add_field(name="🍱 Dish type", value=formatted_dish_types, inline=True)

        if cuisines:
            formatted_cuisine = "\n".join(f"• {item}" for item in cuisines)
            embed.add_field(name="🌍 Cuisine", value=formatted_cuisine, inline=True)

        if diets:
            formatted_diets = "\n".join(f"• {item}" for item in diets)
            embed.add_field(name="🥗 Diet", value=formatted_diets, inline=True)

        embed.set_footer(text=f"Source name: {source_name}")

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

    logging.info(f"Command '!cuisine' was called with argument: {cuisine}.")


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
        "ranking":1,
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
        source_name=info.get("sourceName", "")
        cuisines = info.get("cuisines", [])
        dish_types = info.get("dishTypes", [])
        price = info.get("pricePerServing", 0)
        diets = info.get("diets", [])


        embed = discord.Embed(
            title=title,
            url=source_url,
            colour=discord.Colour.blurple()
        )
        embed.add_field(name="🛒 Missed Ingredients", value=missed_ingredients, inline=False)
        embed.add_field(name="🍽️ Servings", value=servings, inline=True)
        embed.add_field(name="⏱️ Ready in",value=f"{ready_in} minutes",inline=True)

        embed.add_field(name="💰 Price Per Serving", value=f"{price / 100:.2f} USD", inline=True)
        if dish_types:
            formatted_dish_types = "\n".join(f"• {item}" for item in dish_types)
            embed.add_field(name="🍱 Dish type", value=formatted_dish_types, inline=True)

        if cuisines:
            formatted_cuisine = "\n".join(f"• {item}" for item in cuisines)
            embed.add_field(name="🌍 Cuisine", value=formatted_cuisine, inline=True)

        if diets:
            formatted_diets = "\n".join(f"• {item}" for item in diets)
            embed.add_field(name="🥗 Diet", value=formatted_diets, inline=True)

        embed.set_footer(text=f"Source name: {source_name}")

        embed.set_image(url=image_url)
        embed.set_footer(text=f"Source name: {source_name}")

        ingredients = info.get("extendedIngredients", [])

        ingredient_list = []
        for item in ingredients:
            name = item.get("name", "unknown")
            amount = item.get("amount", 0)
            unit = item.get("unit", "")
            if name in missed_ingredients:
                ingredient_list.append(f"• **{amount} {unit} {name} - missing**".strip())
            else:
                ingredient_list.append(f"• {amount} {unit} {name}".strip())


        formatted_ingredients = "\n".join(ingredient_list)

        instructions_raw = info.get("instructions", "")
        analyzed_instructions = info.get("analyzedInstructions", [])
        instructions = ""

        if instructions_raw and is_html(instructions_raw):
            cleaner = HTMLCleaner()
            instructions = cleaner.clean(instructions_raw)

        if analyzed_instructions:
            steps = []
            for step in analyzed_instructions[0].get("steps", []):
                steps.append(f"{step['number']}. {step['step']}")
            instructions = "\n".join(steps)

        if not instructions:
            instructions = "No instructions available 😢"

        msg = await sender(ctx, embed=embed)
        if msg:
            await msg.add_reaction("❤️")

        await ctx.send(f"📋 **Ingredients:**\n{formatted_ingredients}\n")
        await ctx.send(f"\n📖 **Instructions for {title}:**\n{instructions}")

    logging.info(f"Command '!ingredients' was called with argument: {ingredients}.")

@bot.command(name="random")
async def random_recipe(ctx, number:int=1):
    if number < 1 or number > 5:
        await ctx.send("❗ Please request between 1 and 5 recipes.")
        return

    url = "https://api.spoonacular.com/recipes/random"

    params = {
        "number": number,
        "apiKey": API_KEY,
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        await ctx.send("⚠️ Failed to get recipes.")
        return

    data = response.json()
    recipes = data["recipes"]

    for recipe in recipes:
        title = recipe["title"]
        image_url = recipe.get("image", "Unknown")
        source_url = recipe.get("sourceUrl", "")
        servings = recipe.get("servings", 0)
        ready_in_minutes = recipe.get("readyInMinutes", 0)
        cuisines = recipe.get("cuisines", [])
        dish_types = recipe.get("dishTypes", [])
        price = recipe.get("pricePerServing", 0)
        diets = recipe.get("diets", [])
        source_name=recipe.get("sourceName", "")

        embed = discord.Embed(
            title=title,
            url=source_url,
            color=discord.Color.green()
        )

        embed.add_field(name="🍽️ Servings",value=servings,inline=True)
        embed.add_field(name="⏱️ Ready in",value=f"{ready_in_minutes} minutes",inline=True)
        embed.add_field(name="💰 Price Per Serving",value=f"{price/100:.2f} USD",inline=True)
        if dish_types:
            formatted_dish_types = "\n".join(f"• {item}" for item in dish_types)
            embed.add_field(name="🍱 Dish type", value=formatted_dish_types, inline=True)

        if cuisines:
            formatted_cuisine = "\n".join(f"• {item}" for item in cuisines)
            embed.add_field(name="🌍 Cuisine",value=formatted_cuisine,inline=True)

        if diets:
            formatted_diets = "\n".join(f"• {item}" for item in diets)
            embed.add_field(name="🥗 Diet",value=formatted_diets,inline=True)
        embed.set_footer(text=f"Source name: {source_name}")

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
        name="`!recipe <name>`",
        value="🔍 Searches for a recipe by name and shows a random matching result.\nExample: `!recipe pasta`",
        inline=False
    )

    embed.add_field(
        name="`!meal <meal type> [number]`",
        value="🍽️ Searches for random recipes by type (e.g. breakfast, maincourse ). Optional number (1-5). "
              "\nExample: `!meal breakfast 2`"
              "\n**Available meal types**: `maincourse`, `sidedish`, `dessert`, `appetizer`, `salad`, `bread`, `breakfast`, `soup`, `beverage`, `sauce`, `marinade`, `fingerfood`, `snack`, `drink`. ",

        inline=False
    )

    embed.add_field(
        name="`!cuisine <cuisine type> [number]`",
        value="🌍 Searches for recipes from a specific cuisine. Optional number (1-5). "
              "\nExample: `!cuisine italian 3`"
              "\n**Available cuisines**: `african`, `asian`, `american`, `british`, `cajun`, `caribbean`, `chinese`, `easterneuropean`, `european`, `french`, `german`, `greek`, `indian`, `irish`, `italian`, `japanese`, `jewish`, `korean`, `latinamerican`, `mediterranean`, `mexican`, `middleeastern`, `nordic`, `southern`, `spanish`, `thai`, `vietnamese`. ",
        inline=False
    )

    embed.add_field(
        name="`!ingredients <ingredient1,ingredient2,...> [number]`",
        value="🧂 Finds recipes based on available ingredients.\nExample: `!ingredients tomato,cheese 2`",
        inline=False
    )

    embed.add_field(
        name="`!random [1-5]`",
        value="🎲 Shows 1 to 5 random recipes.\nExample: `!random 3`",
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
