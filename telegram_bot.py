import subprocess
import os
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import schedule
import time

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHANNEL_ID')
REPO_OWNER = 'frappe'
REPO_NAME = 'frappe'
BRANCH_VERSION_14 = 'version-14'
BRANCH_VERSION_15 = 'version-15'
REPO_NAME_FRAPPE = 'frappe/frappe'
REPO_NAME_ERPNEXT = 'frappe/erpnext'
def last_commit(update: Update, context: CallbackContext, repo_name: str) -> None:
    github_api_url = f'https://api.github.com/repos/{repo_name}/commits'
    
    response = requests.get(github_api_url)

    if response.status_code == 200:
        commit_data = response.json()[0]  
        commit_message = commit_data['commit']['message'][:200]

        context.bot.send_message(chat_id=CHAT_ID, text=f'Last commit for {repo_name}:\n\n{commit_message}')
    else:
        context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to fetch last commit for {repo_name} from GitHub.')


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot started. Polling for new commits...')

def commits(update: Update, context: CallbackContext) -> None:
    tag = context.args[0] if context.args else None

    if not tag:
        update.message.reply_text('Please provide a tag name. Example: /commits v1.0.0')
        return

    github_api_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits'
    github_api_url += f'?sha={tag}'

    response = requests.get(github_api_url)

    if response.status_code == 200:
        commits_data = response.json()[:5]  
        commit_messages = [commit['commit']['message'] for commit in commits_data]

        message = "\n\n".join(commit_messages)

        context.bot.send_message(chat_id=CHAT_ID, text=f'Commits for tag {tag}:\n\n{message}')
    else:
        context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to fetch commits for tag {tag} from GitHub.')


def last_commit_in_branch(update: Update, context: CallbackContext, repo_name: str, branch_name: str) -> None:
    github_api_url = f'https://api.github.com/repos/{repo_name}/commits'
    github_api_url += f'?sha={branch_name}'

    response = requests.get(github_api_url)

    if response.status_code == 200:
        commit_data = response.json()[0]
        commit_message = commit_data['commit']['message']

        context.bot.send_message(chat_id=CHAT_ID, text=f'Last commit for {repo_name} in {branch_name}:\n\n{commit_message}')
    else:
        context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to fetch last commit for {repo_name} in {branch_name} from GitHub.')

def last_commit_version_14(update: Update, context: CallbackContext) -> None:
    last_commit_in_branch(update, context, REPO_NAME_FRAPPE, BRANCH_VERSION_14)

def last_commit_version_15(update: Update, context: CallbackContext) -> None:
    last_commit_in_branch(update, context, REPO_NAME_FRAPPE, BRANCH_VERSION_15)

def last_commit_erpnext_version_14(update: Update, context: CallbackContext) -> None:
    last_commit_in_branch(update, context, REPO_NAME_ERPNEXT, BRANCH_VERSION_14)

def last_commit_erpnext_version_15(update: Update, context: CallbackContext) -> None:
    last_commit_in_branch(update, context, REPO_NAME_ERPNEXT, BRANCH_VERSION_15)



def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("commits", commits, pass_args=True))
    dp.add_handler(CommandHandler("last_commit_version_14", last_commit_version_14))
    dp.add_handler(CommandHandler("last_commit_version_15", last_commit_version_15))
    dp.add_handler(CommandHandler("last_commit_erpnext_version_14", last_commit_erpnext_version_14))
    dp.add_handler(CommandHandler("last_commit_erpnext_version_15", last_commit_erpnext_version_15))
    updater.start_polling()

    updater.idle()
    schedule.every().minute.do(job) 

    updater.start_polling()

    try:
        timeout = time.time() + 60 
        while time.time() < timeout:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        updater.stop()
        print("Bot stopped by the user.")
if __name__ == '__main__':
    main()
