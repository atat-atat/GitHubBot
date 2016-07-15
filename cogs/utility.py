import discord
from discord.ext import commands
from urllib.parse import quote
import urllib.request
import aiohttp
import os

class UtilityCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def latex(self, *text):
        """Converts unformated LaTeX into an image
        http://estudijas.lu.lv/pluginfile.php/14809/mod_page/content/16/instrukcijas/matematika_moodle/LaTeX_Symbols.pdf"""
        url = "http://latex.codecogs.com/png.latex?\\bg_white \\huge "
        latex = ""

        for token in list(text):
            url += " " + quote(token)

        url = url.replace(' ', "%20")

        urllib.request.urlretrieve(url, "./cogs/latex_image.png")

        await self.bot.upload('./cogs/latex_image.png')
        os.remove('./cogs/latex_image.png')

def setup(bot):
    bot.add_cog(UtilityCog(bot))