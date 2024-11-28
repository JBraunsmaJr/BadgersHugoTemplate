import os
import argparse
from time import sleep
from typing import Final

SCRIPT_DIR: Final[str] = os.path.dirname(os.path.realpath(__file__))
CONTAINER_NAME: Final[str] = "blogsite"
CONTAINER_COMMAND_PREFIX: Final[str] = f"docker exec {CONTAINER_NAME}"
WEBSITE_PATH: Final[str] = os.path.join(SCRIPT_DIR, "website")

def is_container_running() -> bool:
    return len(os.popen(f"docker ps -q --filter name={CONTAINER_NAME}").read().strip()) > 0

def is_image_present() -> bool:
    return len(os.popen(f"docker images -q badgers-hugo-template -q").read().strip()) > 0

def build_image():
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

def update_env_variables(variables: dict[str, str]):
    with open(os.path.join(SCRIPT_DIR, ".env"), "w") as f:
        for variable_name, value in variables.items():
            f.write(f"{variable_name}={value}\n")

def install_theme(theme_name: str, golang_module: str, github_url: str):
    # Must initialize the golang module
    run_command_in_container(f"hugo mod get  {golang_module}")
    
    if not os.path.exists(os.path.join(SCRIPT_DIR, ".git")):
        print("Git repository was not initialized. Doing that now...")
        os.system("git init")
    
    if not os.path.exists(os.path.join(SCRIPT_DIR, ".gitmodules")):
        # Then must add this as a submodule
        os.system("git submodule init")        
    
    os.system(f"git submodule add -f \"{github_url}\" {os.path.join('website', 'themes', theme_name)}")       
    update_env_variables({"THEME_NAME": theme_name})
    restart_container()

if not is_image_present():
    build_image()

parser = argparse.ArgumentParser()

# This argument is only valid if the go module hasn't been initialized (or the website)
parser.add_argument(
    "--sitename",
    default=None,
    dest="sitename", 
    required=not has_go_module_been_initialized())

parser.add_argument("--theme",
                    dest="theme",
                    default=None,
                    required=False,
                    help="The name of the theme to use")

parser.add_argument("--install-theme",
                    dest="install_theme",
                    required=False,
                    default=None,
                    help="The name of the theme to install")

parser.add_argument("--install-theme-gomod",
                    dest="install_theme_gomod",
                    required=False,
                    default=None,
                    help="Golang module to add")

parser.add_argument("--install-theme-github",
                    dest="install_theme_github",
                    required=False,
                    default=None,
                    help="Github URL for github submodule")

args = parser.parse_args()

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

if args.sitename is not None:
    run_command_in_container(f"hugo mod init {args.sitename}")
    os.makedirs(os.path.join(WEBSITE_PATH, "content", "posts"))
    with open(os.path.join(WEBSITE_PATH, "content", "posts", "FirstPost.md"), "w") as f:
        f.write("""First Post
        
        I have some content!
        """)

if args.theme is not None:
    update_env_variables({"THEME_NAME": args.theme})
    restart_container()

if args.install_theme or args.install_theme_gomod or args.install_theme_github:
    errors: list[str] = []
    # Ensure all 3 are present
    if not args.install_theme:
        errors.append("--install-theme")
    if not args.install_theme_gomod:
        errors.append("--install-theme-gomod")
    if not args.install_theme_github:
        errors.append("--install-theme-github")
    
    if errors:
        print(f"Must specify {', '.join(errors)} as well")
        exit(1)
    
    install_theme(args.install_theme, args.install_theme_gomod, args.install_theme_github)