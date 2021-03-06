from discord.ext import commands
import discord
import asyncio
import aiohttp
import json
import sys
import traceback
import feedparser

with open('config.json', 'r') as f:
	settings = json.load(f)

class GitHubCog:
	def __init__(self, bot):
		self.bot = bot
		self.repo_data = {}
		self.repo_issues = {}

	@commands.group(pass_context=True, no_pm=True)
	async def github(self, ctx):
		"""
		GitHub management commands.
		"""
		if ctx.invoked_subcommand is None:
			await self.bot.say("You must provide a subcommand.\nUse $help github for more information.")

	@github.error
	async def github_error(self, error, ctx):
		if isinstance(error, commands.NoPrivateMessage):
			await self.bot.say("You can not use this command in a private message!")
			return
	
	@github.command(name="add_repo", pass_context=True)
	async def github_add_repo(self, ctx, repo_owner : str, repo_name : str):
		"""
		Notifies users when a repository has a new commit.
		"""
		async with aiohttp.get('https://api.github.com/repos/{}/{}/commits?per_page=1?client_id={}?client_secret={}?{}'.format(repo_owner, repo_name, settings['github']['client_id'], settings['github']['client_secret'], settings['github']['access_token'])) as r:
			response = await r.json()

		if 'message' in response:
			if response['message'] == "Not Found":
				await self.bot.say("That repository does not exist.")
				return

		with open('./cogs/github_info.json', 'r') as f:
			config = json.load(f)

		if ctx.message.server.id not in config['repositories']:
			config['repositories'][ctx.message.server.id] = {}
			config['repositories'][ctx.message.server.id][ctx.message.channel.id] = {}

		elif ctx.message.channel.id not in config['repositories'][ctx.message.server.id]:
			config['repositories'][ctx.message.server.id][ctx.message.channel.id] = {}

		if repo_owner in config['repositories'][ctx.message.server.id][ctx.message.channel.id]:
			if repo_name in config['repositories'][ctx.message.server.id][ctx.message.channel.id][repo_owner]:
				await self.bot.say("That repository has already been added.")
				return
			else:
				config['repositories'][ctx.message.server.id][ctx.message.channel.id][repo_owner].append(repo_name)
		else:
			config['repositories'][ctx.message.server.id][ctx.message.channel.id][repo_owner] = []
			config['repositories'][ctx.message.server.id][ctx.message.channel.id][repo_owner].append(repo_name)

		with open('./cogs/github_info.json', 'w') as f:
			json.dump(config, f)

		await self.bot.say("You will now receive notifications when a new commit has been pushed from this repository, or if an issue was filed.")

	@github.command(name='del_repo', pass_context=True, no_pm=True)
	async def github_remove_repo(self, ctx, repo_owner : str, repo_name : str=None):
		"""
		Disables notifications from a repository.
		"""
		with open('./cogs/github_info.json', 'r') as f:
			config = json.load(f)

		if ctx.message.server.id not in config['repositories']:
			await self.bot.say("No repositories have been added on this server.")
			return
		elif ctx.message.channel.id not in config['repositories'][ctx.message.server.id]:
			await self.bot.say("No repositories have been added in this channel.")
			return
		elif repo_owner not in config['repositories'][ctx.message.server.id][ctx.message.channel.id]:
			await self.bot.say("No repositories have been added from that owner in this channel.")
			return
		elif repo_name not in config['repositories'][ctx.message.server.id][ctx.message.channel.id][repo_owner] and repo_name != None:
			await self.bot.say("That repository has not been added.")
			return

		if repo_name == None:
			config['repositories'][ctx.message.server.id][ctx.message.channel.id].pop(repo_owner)
		else:
			config['repositories'][ctx.message.server.id][ctx.message.channel.id][repo_owner].remove(repo_name)

		with open('./cogs/github_info.json', 'w') as f:
			json.dump(config, f)

		await self.bot.say("You will no longer receive notifications about this repository.")

	@commands.group(aliases=["clear", "clean"], pass_context=True)
	async def purge(self, ctx):
		"""
		Cleans a chat.
		"""
		if ctx.invoked_subcommand is None:
			if ctx.subcommand_passed is None:
				await self.bot.say("You must provide the amount of messages you wish to clear.")
				return

			try:
				amount = int(ctx.subcommand_passed)
			except ValueError:
				await self.bot.say("Invalid amount.")
				return

			await self.bot.purge_from(ctx.message.channel, limit=amount+1)

	@purge.command(name="contains", pass_context=True)
	async def purge_contains(self, ctx, keyword : str, amount : int=50):
		"""
		Cleans the chat if a keyword is in a message.
		"""
		await self.bot.purge_from(ctx.message.channel, limit=amount+1)

	@purge.command(name="member", pass_context=True)
	async def purge_member(self, ctx, member : discord.Member, amount : int=50):
		"""
		Cleans messages sent by a member.
		"""
		def is_mem(m):
			if m == ctx.message or m.author == member:
				return True
			else:
				return False

		await self.bot.purge_from(ctx.message.channel, limit=amount+1, check=is_mem)

	async def git_loop(self):
		"""
		The main GitHub loop.

		This checks whether a new commit has been pushed or not from a repository.
		"""
		while not self.bot.is_closed:
			if 'no-git-loop' in sys.argv:
				return
			try:
				with open('./cogs/github_info.json', 'r') as f:
					git_json = json.load(f)

				for server in git_json["repositories"]:
					for channel in git_json["repositories"][server]:
						for repo_owner in git_json["repositories"][server][channel]:
							for repo in git_json["repositories"][server][channel][repo_owner]:

								d = feedparser.parse('https://github.com/{}/{}/commits/master.atom'.format(repo_owner, repo))
								if 'bozo_exception' in d: #if rss url is invalid
									await self.bot.send_message(discord.Object(channel), "Error while retrieving data from URL: '{}'".format(rss_url))
								else:
									latest_commit = d["entries"][0]["link"]
									fmt = "{} @here".format(latest_commit)
									if channel not in self.repo_data:
										self.repo_data[channel] = {}
										self.repo_data[channel][repo] = latest_commit
										await self.bot.send_message(discord.Object(channel), fmt)

									elif repo not in self.repo_data[channel]:
										self.repo_data[channel][repo] = latest_commit
										await self.bot.send_message(discord.Object(channel), fmt)

									elif self.repo_data[channel][repo] != latest_commit:
										self.repo_data[channel][repo] = latest_commit
										await self.bot.send_message(discord.Object(channel), fmt)

			except Exception as e:
				print("LOOP_ERROR@git_loop! " + self.return_traceback(*sys.exc_info()))
			
			await asyncio.sleep(20)

	def return_traceback(self, etype, value, tb, limit=None, file=None, chain=True):
		if file is None:
			file = sys.stderr
		exceptions = []
		for line in traceback.TracebackException(
				type(value), value, tb, limit=limit).format(chain=chain):
			exceptions.append(line)
		return "\n".join(exceptions)

def setup(bot):
	bot.add_cog(GitHubCog(bot))