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

You will need to update the [compose.yml](./compose.yml) to point towards your GitHub info!

![username to change](./resources/username_to_change.png)

This is easy, it should match the url after `github.com`

![url](./resources/url.png)

You may have noticed a few workflows were included. This is why the prior step is important.
The workflow automatically pulls this information

1. [docker-image.yml](./.github/workflows/docker-image.yml) - This is the docker image that'll run hugo!
2. 

## Setup.py

Everything is set via `config.json`. There are some reasonable defaults which follows NetworkChuck's video. It is worth noting
if you're deploying to github pages you need to change the baseUrl to be whatever your repository name is. For instance, for me, I have
to put `/BadgersBlog` - because that's the repo name I'm using for my blog. Not doing this will result in some weirdness such as

- Paths not working
- Themes! Themes won't work properly! You'll have content, but it won't look.... pretty

How to get started:

Confirm the things in the `config.json` are okay then run the setup script with the `--init` flag.

```bash
python ./setup.py --init
```

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

## Push Deployment

The local version used for testing/development is leveraging localhost:1313. We need to make it work in production environments.
So run the setup script with the `--build` flag. This will update all the hugo project's baseUrl to match what's defined in the 
`config.json`

```bash
python setup.py --build
```

If everything looks okay, run the script with the `--push` flag

```bash
python setup.py --push
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