import discord
from discord.ext import commands
import asyncio
import json

with open('config.json', 'r') as f:
	settings = json.load(f)

if 'description' not in settings:
	description = "A discord bot for GitHub commits and issue tracking, developed by atat."
else:
	description = settings["description"]

bot = commands.Bot(command_prefix=settings['prefix'], description=description)
start_extensions = ['github']
loop = asyncio.get_event_loop()

@bot.event
async def on_ready():
	print("Successfully logged in!")
	print(bot.user.name)
	print(bot.user.id)
	print("--------------")

	for extension in start_extensions:
		if not extension.startswith('cogs.'):
			extension = 'cogs.' + extension

		try:
			bot.load_extension(extension)
		except Exception as e:
			exc = "{}: {}".format(type(e).__name__, e)
			print("Failed to load extension: {}\n{}".format(extension, exc))

	await github_check()

@bot.event
async def on_message(msg):
	fmt = "[{}][{}/#{}][{}]: {}".format(msg.timestamp, msg.server, msg.channel, msg.author, msg.content)
	try:
		print(fmt)
	except UnicodeEncodeError:
		print(fmt.encode('utf-8'))

	await bot.process_commands(msg)

@bot.command(name="reload", pass_context=True)
async def reload_cogs(ctx):
	"""
	Reloads all cogs.
	"""
	for extension in start_extensions:
		if not extension.startswith('cogs.'):
			extension = 'cogs.' + extension

		try:
			bot.unload_extension(extension)
			bot.load_extension(extension)
		except Exception as e:
			exc = "{}: {}".format(type(e).__name__, e)
			await bot.send_message(ctx.message.channel, exc)

	await bot.send_message(ctx.message.channel, ":ok_hand:")

async def github_check():
	if 'cogs.github' in bot.extensions.keys():
		from cogs.github import GitHubCog
		loop.create_task(GitHubCog(bot).git_loop())

if __name__ == '__main__':
	bot.client_id = settings['client_id']

	bot.run(settings['token'])