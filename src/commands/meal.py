import discord
import discord.ext.commands as commands
import os
import requests
import logging
import random

from src.utils.isHTML import is_html
from src.utils.HTMLCleaner import HTMLCleaner
from src.utils.sender import sender


class Meal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("API_KEY")

    @commands.command(name="meal")
    async def search_by_type(self, ctx, *, recipe_type: str):
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

        base_url = "https://api.spoonacular.com/recipes/complexSearch"

        initial_params = {
            "apiKey": self.api_key,
            "type": dish_type,
            "number": 1,
        }
        response = requests.get(base_url, params=initial_params)

        if response.status_code != 200:
            await ctx.send("Failed to get recipes 😕")
            return

        data = response.json()
        total_results = data.get("totalResults", 0)

        if not total_results:
            await ctx.send(f"Cannot find recipes for: **{recipe_type}**")
            return

        if total_results > 1:
            await ctx.send(f"🔎 Matching results: **{total_results}**")

        rand_offset = random.randint(0, max(0, total_results - number))

        params = {
            "type": dish_type,
            "offset": rand_offset,
            "number": number,
            "addRecipeInformation": True,
            "apiKey": self.api_key,
        }

        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            await ctx.send("Failed to get recipe 😕")
            return

        data = response.json()
        results = data.get("results", [])

        for recipe in results:
            title = recipe.get("title", "Unknown recipe")
            image_url = recipe.get("image", "")
            source = recipe.get("sourceUrl", "")
            recipe_id = recipe.get("id", 0)

            embed = discord.Embed(
                title=title, url=source, colour=discord.Colour.blurple()
            )

            if image_url:
                embed.set_image(url=image_url)

            # Instructions
            info_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"

            info_params = {
                "apiKey": self.api_key,
            }
            info_response = requests.get(info_url, params=info_params)
            info_data = info_response.json()

            # Instructions
            instructions_raw = info_data.get("instructions", "")
            analyzed_instructions = info_data.get("analyzedInstructions", [])
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

            # Embed fields
            embed.add_field(
                name="🍽️ Servings", value=info_data.get("servings", 0), inline=True
            )
            embed.add_field(
                name="⏱️ Ready in",
                value=f"{info_data.get('readyInMinutes', 0)} minutes",
                inline=True,
            )
            embed.add_field(
                name="💰 Price Per Serving",
                value=f"{info_data.get('pricePerServing', 0) / 100:.2f} USD",
                inline=True,
            )

            if dish_types := recipe.get("dishTypes"):
                embed.add_field(
                    name="🍱 Dish type",
                    value="\n".join(f"• {item}" for item in dish_types),
                    inline=True,
                )

            if cuisines := recipe.get("cuisines"):
                embed.add_field(
                    name="🌍 Cuisine",
                    value="\n".join(f"• {item}" for item in cuisines),
                    inline=True,
                )

            if diets := recipe.get("diets"):
                embed.add_field(
                    name="🥗 Diet",
                    value="\n".join(f"• {item}" for item in diets),
                    inline=True,
                )

            embed.set_footer(text=f"Source name: {recipe.get('sourceName', '')}")

            # Ingredients
            ingredients = info_data.get("extendedIngredients", [])
            ingredient_list = []

            for item in ingredients:
                name = item.get("name", "unknown")
                amount = item.get("amount", 0)
                unit = item.get("unit", "")
                ingredient_list.append(f"• {amount} {unit} {name}".strip())

            formatted_ingredients = "\n".join(ingredient_list)

            # Message sending
            msg = await sender(ctx, embed=embed)
            if msg:
                await msg.add_reaction("❤️")

            header = f"\n📖 **Instructions for {title}:**\n"
            max_instr_lenght = 2000 - len(header) - 3

            await ctx.send(f"📋 **Ingredients:**\n{formatted_ingredients}\n")

            if len(instructions) >= 2000:
                await ctx.send(f"{header}{instructions[:max_instr_lenght]}" + "...")
            else:
                await ctx.send(f"{header}{instructions}")

        logging.info(f"Command '!cuisine' was called with argument: {dish_type}.")


async def setup(bot):
    await bot.add_cog(Meal(bot))
