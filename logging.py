import wandb
import json

with open('config.json', 'r') as file:
    config = json.load(file)

def init(exp_tags):

    if config['logging']:
        with open('wandb_secret.txt', 'r') as file:
            api_key = file.read()
        wandb.login(api_key)
        wandb.init(project="nuclear-hack", tags=exp_tags)

def log_params():
    ...