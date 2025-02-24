from idlelib.configdialog import help_common
from idlelib.debugobj import dispatch

import telegram
from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext)
from ChatGPT_HKBU import HKBU_ChatGPT
import configparser
import logging
import redis

global redis1

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # 调试：打印配置文件内容
    # print("Config sections:", config.sections())
    # if 'REDIS' in config:
    #     print("REDIS HOST:", config['REDIS'].get('HOST'))
    #     print("REDIS PASSWORD:", config['REDIS'].get('PASSWORD'))
    #     print("REDIS PORT:", config['REDIS'].get('PORT'))
    #     print("REDIS DECODE_RESPONSES:", config['REDIS'].get('DECODE_RESPONSES'))
    #     print("REDIS USERNAME:", config['REDIS'].get('USERNAME'))
    # else:
    #     print("REDIS section not found in config.ini")


    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher

    global redis1
    redis1 = redis.Redis(
        host=(config['REDIS']['HOST']),
        password=(config['REDIS']['PASSWORD']),
        port=(config['REDIS']['PORT']),
        decode_responses=(config['REDIS'].getboolean('DECODE_RESPONSES')),
        username=(config['REDIS']['USERNAME'])
    )

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = HKBU_ChatGPT(config)
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command), equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    dispatcher.add_handler(CommandHandler('add', add))
    dispatcher.add_handler(CommandHandler('help', help_command))

    updater.start_polling()
    updater.idle()

def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info('Update:' + str(update))
    logging.info('Context:' + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('How can I help you ?')

def add(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]
        redis1.incr(msg)

        update.message.reply_text('You have said ' + msg + ' for ' + redis1.get(msg) + ' times.')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info('Update:' + str(update))
    logging.info('Context:' + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


if __name__ == '__main__':
    main()