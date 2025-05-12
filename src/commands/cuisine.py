import discord
from discord.ext import commands
import requests
import os
import random
import logging

from src.utils.isHTML import is_html
from src.utils.HTMLCleaner import HTMLCleaner
from src.utils.sender import sender

class Cuisine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('API_KEY')


##todo - wywalić niepotrzebne zapytania, bo da sie to raczej w 1 zrobić
    @commands.command(name="cuisine")
    async def search_by_cuisine(self, ctx, *, cuisine:str):
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
            "apiKey": self.api_key,
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
            "apiKey": self.api_key,
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
                "apiKey": self.api_key,
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

async def setup(bot):
    await bot.add_cog(Cuisine(bot))