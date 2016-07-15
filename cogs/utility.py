import discord
from discord.ext import commands
import urllib

class UtilityCog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def latex(self, *text):
        """Converts unformated LaTeX into an image
        http://estudijas.lu.lv/pluginfile.php/14809/mod_page/content/16/instrukcijas/matematika_moodle/LaTeX_Symbols.pdf"""
        url = "http://latex.codecogs.com/png.latex?\\huge "
        latex = ""

        for token in text:
            url += token.replace("\\", "\\\\")
            
        url = url.replace(' ', '%20')

        latex_image = urllib.request.urlopen(url)
        await bot.send_file(ctx.message.channel, latex_image, filename='latex.png')

def setup(bot):
    bot.add_cog(UtilityCog(bot))