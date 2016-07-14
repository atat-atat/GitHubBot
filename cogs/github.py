from discord.ext import commands
import discord
import asyncio
import aiohttp
import json
import sys
import traceback

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
	async def github_remove_repo(self, ctx, repo_owner : str, repo_name : str):
		"""
		Disables notifications from a repository.
		"""
		pass

	async def git_loop(self):
		"""
		The main GitHub loop.

		This checks whether a new commit has been pushed or not from a repository.
		"""
		while not self.bot.is_closed:
			try:
				with open('./cogs/github_info.json', 'r') as f:
					git_json = json.load(f)

				for server in git_json["repositories"]:
					for channel in git_json["repositories"][server]:
						for repo_owner in git_json["repositories"][server][channel]:
							for repo in git_json["repositories"][server][channel][repo_owner]:

								url = "https://api.github.com/repos/{}/{}/commits?per_page=1?client_id={}?client_secret={}?access_token={}".format(repo_owner, repo, settings['github']['client_id'], settings['github']['client_secret'], settings['github']['access_token'])
								print(url)

								async with aiohttp.get(url) as r:
									response = await r.json()

								if 'message' in response:
									await self.bot.send_message(discord.Object(channel), "MESSAGE RESP: " + response["message"])
								else:

									latest_commit = response[0]["commit"]["message"]
									commit_url = response[0]["html_url"]
									if len(latest_commit) > 30:
										latest_commit = latest_commit[:50] + "..."
									date = response[0]["commit"]["author"]["date"]
									committer = response[0]["commit"]["author"]["name"]
									fmt = "{} --\n{}\n**Pushed by {} ({})**".format(commit_url, latest_commit, committer, date)

									if channel not in self.repo_data:
										self.repo_data[channel] = {}
										self.repo_data[channel][repo] = response[0]["sha"]
										await self.bot.send_message(discord.Object(channel), fmt)
									elif repo not in self.repo_data[channel]:
										self.repo_data[channel][repo] = response[0]["sha"]
										await self.bot.send_message(discord.Object(channel), fmt)
									elif self.repo_data[channel][repo] != response[0]["sha"]:
										self.repo_data[channel][repo] = response[0]["sha"]
										await self.bot.send_message(discord.Object(channel), fmt)

									issues_url = "https://api.github.com/repos/{}/{}/issues?per_page=1?client_id={}?client_secret={}?access_token={}".format(repo_owner, repo, settings['github']['client_id'], settings['github']['client_secret'], settings['github']['access_token'])
									print(issues_url)

									async with aiohttp.get(issues_url) as r:
										response = await r.json()

									if len(response) > 0:
										issue_id = response[0]["id"]
										issue_num = response[0]["number"]
										issue_title = response[0]["title"]
										issue_submitter = response[0]["user"]["login"]
										issue_url = response[0]["html_url"]
										issue_date = response[0]["created_at"]

										fmt = "{} -- *Issue {}*\n{}\n**Issued by {} ({})**".format(issue_url, issue_num, issue_title, issue_submitter, issue_date)

										if channel not in self.repo_issues:
											self.repo_issues[channel] = {}
											self.repo_issues[channel][repo] = issue_id
											await self.bot.send_message(discord.Object(channel), fmt)
										elif repo not in self.repo_issues[channel]:
											self.repo_issues[channel][repo] = issue_id
											await self.bot.send_message(discord.Object(channel), fmt)
										elif self.repo_issues[channel][repo] != issue_id:
											self.repo_issues[channel][repo] = issue_id
											await self.bot.send_message(discord.Object(channel), fmt)

			except Exception as e:
				print("LOOP_ERROR@git_loop! " + self.return_traceback(*sys.exc_info()))
			
			await asyncio.sleep(4000)

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