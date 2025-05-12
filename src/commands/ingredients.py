import discord
from discord.ext import commands
import requests
import os
import logging

from src.utils.isHTML import is_html
from src.utils.HTMLCleaner import HTMLCleaner
from src.utils.sender import sender

class Ingredients(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('API_KEY')

    @commands.command(name="ingredients")
    async def search_by_ingredients(self, ctx, *, ingredients:str):
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
            "apiKey": self.api_key,
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
                "apiKey": self.api_key
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

async def setup(bot):
    await bot.add_cog(Ingredients(bot))