import discord
from discord.ext import commands
import requests
import os
import logging

from src.utils.sender import sender


class Random(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("API_KEY")

    @commands.command(name="random")
    async def random_recipe(self, ctx, number: int = 1):
        if number < 1 or number > 5:
            await ctx.send("❗ Please request between 1 and 5 recipes.")
            return

        url = "https://api.spoonacular.com/recipes/random"

        params = {
            "number": number,
            "apiKey": self.api_key,
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
            source_name = recipe.get("sourceName", "")

            embed = discord.Embed(
                title=title, url=source_url, color=discord.Color.green()
            )

            embed.add_field(name="🍽️ Servings", value=servings, inline=True)
            embed.add_field(
                name="⏱️ Ready in", value=f"{ready_in_minutes} minutes", inline=True
            )
            embed.add_field(
                name="💰 Price Per Serving", value=f"{price/100:.2f} USD", inline=True
            )
            if dish_types:
                formatted_dish_types = "\n".join(f"• {item}" for item in dish_types)
                embed.add_field(
                    name="🍱 Dish type", value=formatted_dish_types, inline=True
                )

            if cuisines:
                formatted_cuisine = "\n".join(f"• {item}" for item in cuisines)
                embed.add_field(name="🌍 Cuisine", value=formatted_cuisine, inline=True)

            if diets:
                formatted_diets = "\n".join(f"• {item}" for item in diets)
                embed.add_field(name="🥗 Diet", value=formatted_diets, inline=True)
            embed.set_footer(text=f"Source name: {source_name}")

            if image_url:
                embed.set_image(url=image_url)

            msg = await sender(ctx, embed=embed)
            if msg:
                await msg.add_reaction("❤️")

        logging.info("Command '!random' was called.")


async def setup(bot):
    await bot.add_cog(Random(bot))
