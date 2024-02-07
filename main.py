import subprocess
import os
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHANNEL_ID')
REPO_OWNER = 'frappe'
REPO_NAME = 'frappe'

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
        commit_messages = [commit['commit']['message'][:200] for commit in commits_data]

        message = "\n\n".join(commit_messages)

        context.bot.send_message(chat_id=CHAT_ID, text=f'Commits for tag {tag}:\n\n{message}')
    else:
        context.bot.send_message(chat_id=CHAT_ID, text=f'Failed to fetch commits for tag {tag} from GitHub.')




def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("commits", commits, pass_args=True))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()
