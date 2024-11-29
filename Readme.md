# Badger's Hugo Template

Inspired by [Network Chuck's](https://github.com/theNetworkChuck/chuckblog) efforts. However, I prefer having certain 
tools containerized. 

The [Dockerfile](./Dockerfile) has everything we need to develop our hugo-website with both golang and hugo.

## Requirements

This requires you to have both Python and Docker installed on your machine.

## Template Setup

Click `Use This Template` at [BadgersHugoTemplate](https://github.com/JBraunsmaJr/BadgersHugoTemplate). 

Clone your newly created repo using this template. The `<> Code` button has a dropdown menu with the various 
options available for cloning. 

There should be 3 Github actions that start running.

1. Initial Setup (this should pass. It updates our compose.yml and config.json with our repository info - otherwise it keeps the template info)
2. Deploy Site (this should fail because we don't have a website directory yet)
3. Docker Image CI (this should hopefully pass? It's possible the Initial Setup needs to finish first before this passes)

Reason why Initial Setup and Docker Image CI are separate is because the Initial Setup workflow is no longer needed
once it passes the first time.

Feel free to delete the [validate.yml](.github/workflows/validate.yml) once the action is complete.

## Setup.py

Everything is set via `config.json`. There are some reasonable defaults which follows NetworkChuck's video. It is worth noting
if you're deploying to GitHub pages you need to change the baseUrl to be whatever your repository name is. For instance, for me, I have
to put `/BadgersBlog` - because that's the repo name I'm using for my blog. Not doing this will result in some weirdness such as

- Paths not working
- Themes! Themes won't work properly! You'll have content, but it won't look.... pretty

How to get started:

Confirm the things in the `config.json` are okay then run the setup script with the `--init` flag.

```bash
python ./setup.py --init
```

Now, for the most part, you only have to worry about adding content to your [posts](website/content/posts) directory (website/content/posts)

Feel free to navigate to `http://localhost:1313` to validate everything is working. Otherwise, we're ready to
commit! 

```bash
git add .
git commit -m "Some message you want"
git push origin master
```

This should kick off a GitHub action! When it finishes you should have a new branch `github-pages`. 

On GitHub, go to your repo settings -> Pages.
Select the branch `github-pages` and hit save! This should kick off another GitHub action which deploys 
your static site!

That's it! Now anytime you upload new content your GitHub pages will stay in sync!

----

[Hugo Themes](https://themes.gohugo.io/)

There are three values required per theme you want to try/install. The name, GitHub Url, and the golang module name.
The setup script will automatically initialize your submodules, add the theme where it needs to go and update the 
`.env` to specified theme name. It then restarts the container so the theme changes take over.

Note: You may have to verify the `hugo.toml` file within the `website` directory. For terminal, it's included for 
convenience and automatically pulled in if used.

[Terminal (Default Theme)](https://themes.gohugo.io/themes/hugo-theme-terminal/) just like NetworkChuck.

----

If you have multiple themes and would like to swap between them, use `--theme` argument. This will update the `.env` and
restart the container.

```bash
python ./setup.py --theme terminal
```

## Live Reload

Go to [http://localhost:1313](http://localhost:1313) and you should see content! As you make changes to your markdown files you should see your changes in near-real-time.

## Manage Container

If you aren't trying to configure anything, and want to manage the container

**Start container:**

```bash
docker compose up -d
```

**Stop container:**

```bash
docker compose down
````