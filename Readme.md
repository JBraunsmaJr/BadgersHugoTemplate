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

## Setup.py

What do you want to name your site? -- This is a go module name, so avoid spaces and special characters.

Example: 

```bash
python ./setup.py --sitename badgers-corner
```

----

[Hugo Themes](https://themes.gohugo.io/)

The following three parameters are required if you want to install a theme. 
They work together to do multiple things at once. For example’s sake, we're using
[Terminal](https://themes.gohugo.io/themes/hugo-theme-terminal/) just like NetworkChuck.

| Parameter | Description | Example value |
| --- | --- | --- |
| --install-theme | Name of theme to install | terminal |
| --install-theme-gomod | Go module name | github.com/panr/hugo-theme-terminal/v4 |
| --insstall-theme-github | Github URL to submodule | https://github.com/panr/hugo-theme-terminal.git |

The following command will install the `terminal` theme and update the `.env` file to use `terminal`. 

```bash
python ./setup.py --install-theme terminal --install-theme-gomod github.com/panr/hugo-theme-terminal/v4 --install-theme-github https://github.com/panr/hugo-theme-terminal.git themes/terminal
```

Within the template we have `terminal-hugo.toml`, you'll want to replace the `hugo.toml` in the website directory with that.

----

If you have multiple themes and would like to swap between them, use `--theme` argument. This will update the `.env` and
restart the container.

```bash
python ./setup.py --theme terminal
```

## Live Reload

Go to `http://localhost:1313` and you should see content! As you make changes to your markdown files you should see your changes in near-real-time.