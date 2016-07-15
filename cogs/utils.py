from discord.ext import commands

def has_permissions(**perms):
	def predicate(ctx):
		member = perms.get("member", ctx.message.author)
		if ctx.message.author == ctx.message.server.owner:
			return True
			
		channel = ctx.message.channel
		resolved = channel.permissions_for(member)
		return all(getattr(resolved, name, None) == value for name, value in perms.items())

	return commands.check(predicate)