# GitHubBot
A somewhat multifunctional bot that cleans chats, outputs latex images, and notifies users when a new commit or issue has been filed from a GitHub repository.

To get notifications about new issues and commits from a repo, type `{p}github add_repo {repo_owner} {repo_name}` in the text channel you want to receive notifications from (this will not work in a private message.)

To set your bot up, open up the config.json file, and modify as necessary. Then, run bot.py.

The bot is still fresh from the oven, so there may be bugs, and the `del_repo` command does not do anything at the moment.