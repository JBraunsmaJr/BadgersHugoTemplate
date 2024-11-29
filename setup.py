import argparse
import json
import os
import re
from time import sleep
from typing import Final, Any

SCRIPT_DIR: Final[str] = os.path.dirname(os.path.realpath(__file__))
CONTAINER_NAME: Final[str] = "blogsite"
CONTAINER_COMMAND_PREFIX: Final[str] = f"docker exec {CONTAINER_NAME}"
WEBSITE_PATH: Final[str] = os.path.join(SCRIPT_DIR, "website")
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")

def extract_image_name():
    pattern = r'image:\s*([\w\-\.\/:]+)'

    with open(os.path.join(SCRIPT_DIR, "compose.yml"), "r") as f:
        compose_contents = f.read()

    match = re.search(pattern, compose_contents)

    if match:
        return match.group(1)
    else:
        raise ValueError("Was unable to determine username from compose.yml")

IMAGE_NAME: Final[str] = extract_image_name()

def is_container_running() -> bool:
    return len(os.popen(f"docker ps -q --filter name={CONTAINER_NAME}").read().strip()) > 0

def is_image_present() -> bool:
    return len(os.popen(f"docker images -q {IMAGE_NAME}").read().strip()) > 0

def build_image():
    # Try to pull it first, should pull from github registry
    os.system("docker compose pull")

    if not is_image_present():
        os.system("docker compose build")

def run_command_in_container(command: str):
    os.system(f"{CONTAINER_COMMAND_PREFIX} {command}")

def has_website():
    return os.path.exists(WEBSITE_PATH) and os.listdir(WEBSITE_PATH)

def has_go_module_been_initialized():
    return os.path.exists(os.path.join(WEBSITE_PATH, "go.mod"))

def start_container():
    os.system("docker compose up -d")

def stop_container():
    os.system("docker compose down")

def restart_container():
    stop_container()
    start_container()

# Read the file and remove the BOM if present
def ensure_no_bom(file_path):
    """
    Discovered certain editors / systems may add a nasty little character
    ï»¿  <--- That thing
    Which is a byte order mark (BOM). Indicates file formatting which will break json
    parsing
    """
    with open(file_path, "rb") as f:
        content = f.read()
    # Remove BOM if it exists
    content = content.lstrip(b'\xef\xbb\xbf')
    # Write the cleaned content back to the file
    with open(file_path, "wb") as f:
        f.write(content)

def get_config() -> dict[str, Any]:
    ensure_no_bom(os.path.join(SCRIPT_DIR, "config.json"))
    with open(os.path.join(SCRIPT_DIR, "config.json"), "r") as f:
        contents = json.load(f)
    return contents

def set_config(variables: dict[str, Any]) -> dict[str, Any]:
    variables.update(get_config())
    with open(os.path.join(SCRIPT_DIR, "config.json"), "w") as f:
        f.write(json.dumps(variables))
    return variables


def update_env_variables(variables: dict[str, str | bool]):
    if os.path.exists(ENV_FILE):
        with open(os.path.join(SCRIPT_DIR, ".env"), "r") as f:
            contents = {name: value for name, value in [x.split('=') for x in f.readlines() if len(x.strip()) > 1]}
    else:
        contents = {}

    for key, value in variables.items():
        contents[key] = value

    with open(os.path.join(SCRIPT_DIR, ".env"), "w") as f:
        for variable_name, value in contents.items():
            f.write(f"{variable_name}={value}\n")

def set_deploy_site(value: bool):
    update_env_variables({"DEPLOY": value})

def wait_for_container():
    while is_container_running():
        sleep(0.5)

def initialize_repository():
    if not os.path.exists(os.path.join(SCRIPT_DIR, ".git")):
        print("Git repository was not initialized. Doing that now...")
        os.system("git init")

    if not os.path.exists(os.path.join(SCRIPT_DIR, ".gitmodules")):
        print("Git submodules not initialized. Doing that now...")
        os.system("git submodule init")

    config = get_config()

    if "goSubName" in config and config["goSubName"] is not None and not has_go_module_been_initialized():
        run_command_in_container(f"hugo mod init {config['goSubName']}")
    elif not has_go_module_been_initialized():
        print(f"Must set goSubName in config.json...")
        exit(1)

    default_theme: str | None = None

    if "themes" in config and len(config["themes"]) > 0:
        for theme in config["themes"]:
            default_theme = theme["name"]
            run_command_in_container(f"hugo mod get {theme['moduleName']}")
            theme_name = theme["name"]
            url = theme["githubUrl"]
            os.system(f"git submodule add -f \"{url}\" {os.path.join('website', 'themes', theme_name)}")

            # if we're using terminal we'll automatically copy our config over for it
            if theme_name.lower() == "terminal":
                with open(os.path.join(SCRIPT_DIR, "terminal-hugo.toml"), "r") as f:
                    terminal_config_contents = f.read()
                with open(os.path.join(WEBSITE_PATH, "hugo.toml"), "w") as f:
                    f.write(terminal_config_contents)

    if not os.path.exists(os.path.join(WEBSITE_PATH, "content", "posts")):
        os.makedirs(os.path.join(WEBSITE_PATH, "content", "posts"))
        with open(os.path.join(WEBSITE_PATH, "content", "posts", "FirstPost.md"), "w") as f:
            f.write("""First Post
I have some content!
        """)
    # Must restart container if theme changes
    if "theme" in config and config["theme"] is not None:
        update_env_variables({"THEME": config["theme"]})
        restart_container()
    elif default_theme is not None:
        update_env_variables({"THEME": default_theme})
        restart_container()


if not is_image_present():
    build_image()

parser = argparse.ArgumentParser()

parser.add_argument("--theme",
                    dest="theme",
                    default=None,
                    required=False,
                    help="The name of the theme to use")

parser.add_argument("--build",
                    dest="build",
                    required=False,
                    default=False,
                    help="Builds the site so that it can be deployed",
                    action="store_true")

parser.add_argument("--init",
                    dest="init",
                    required=False,
                    default=None,
                    action="store_true",
                    help="Initialize the project via config.json")


args = parser.parse_args()

if args.build is True:
    if not is_image_present():
        print("Image must be present in order to deploy:\n\n"
              f"Expected: {IMAGE_NAME}\n"
              f"Currently Present: {os.popen('docker images')}")
        exit(1)

    if is_container_running():
        stop_container()

    toml_path = os.path.join(WEBSITE_PATH, "hugo.toml")

    with open(toml_path, "r") as f:
        previous_toml_content = f.read()

    config = get_config()
    base_url = config["baseUrl"]
    # Regex to match 'baseurl = "<value>"'
    updated_content = re.sub(
        r'(?m)^baseurl\s*=\s*".*"',  # Match 'baseurl = "<value>"' at the beginning of the line
        f'baseurl = "{base_url}"',  # Replace with the new baseurl
        previous_toml_content
    )

    with open(toml_path, "w") as f:
        f.write(updated_content)

    set_deploy_site(True)

    # Ensure our container is turned off
    stop_container()

    start_container()
    wait_for_container()
    set_deploy_site(False)

    # Reset our toml file
    with open(toml_path, "w") as f:
        f.write(updated_content)

    exit()


def ensure_container_is_running():
    # BASELINE - CONTAINER SHOULD BE RUNNING
    if not is_container_running():
        # We'll see if we can start it programmatically
        try:
            start_container()
        except Exception as ex:
            print(f"Was unable to start container...\n{ex}\n\n"
                  f"Please run `docker compose up -d` then try again...")
            exit(1)
        print("Waiting for container to settle down...")
        sleep(5)
        if not is_container_running():
            print(f"Container {CONTAINER_NAME} must be running.\n\n"
                  f"Please run `docker compose up -d")
            exit(1)

if args.init is True:
    # Just to initialize it 
    # we specified it in our compose file so it must be present
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            f.write('')
    ensure_container_is_running()
    initialize_repository()
else:
    ensure_container_is_running()

if args.theme is not None:
    update_env_variables({"THEME_NAME": args.theme})
    restart_container()
