import discord
from discord.ext import commands
import requests
import os
import logging

class Helpme(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv('API_KEY')

    @commands.command(name="helpme")
    async def help_command(self, ctx):
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

        logging.info(f"Command '!helpme' was called.")

async def setup(bot):
    await bot.add_cog(Helpme(bot))