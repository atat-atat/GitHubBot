# GitHubBot
A somewhat multifunctional Discord bot that cleans chats, outputs latex images, and notifies users when a new commit or issue has been filed from a GitHub repository.

To get notifications about new issues and commits from a repo, type `{p}github add_repo {repo_owner} {repo_name}` in the text channel you want to receive notifications from (this will not work in a private message.)

If you no longer want to receive notifications from a repository, then you can use `{p}github del_repo {repo_owner} {repo_name}`, or if you want to remove all notifications from repositories created by a specific owner, then you can simply use `{p}github del_repo {repo_owner}`.

To set your bot up, open up the config.json file, and modify as necessary. Then, run bot.py.

The bot is still fresh from the oven, so there may be bugs, and the `del_repo` command does not do anything at the moment.