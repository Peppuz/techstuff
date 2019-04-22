import requests
import logging
import json
# import mechanize
import telegram
import time
import datetime
from lxml.html import fromstring
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


admin = [135605474, 311495487] # 311495487 
channel_id = "-1001480479440"
FIFO = []
try:
    with open('fifo.json') as ff:
            FIFO = json.load(ff)
            print("[INFO] Queue loaded correctly")

except:
    print("[ERR] creating a new queue file")
    with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)


def start(bot, update):
    update.message.reply_text('Hi!')


def send_link(bot, job):
    try:
        link = FIFO.pop(0)
        print("[INFO] Getting link's title")
        # title grabber with requests 
        r = requests.get(link)
        tree = fromstring(r.content)
        title = tree.findtext('.//title')

        # Formatting text
        text = "{} \n\n {}".format(title, link)
        bot.send_message(channel_id, text=text)
        
        # Monitoring
        send_admin(bot, "Link postato, link in queue: %s" % len(FIFO))
        if len(FIFO) == 1:
            send_admin(bot, "1 Articolo rimane da pubblicare, aggiungine altri!")

    except IndexError:
        send_admin(bot, "Lista vuota!!")

    except requests.exceptions.InvalidSchema:
        send_admin(bot, "Link non valido")

    finally: 
        json.dump(FIFO, open('fifo.json', 'w'))


def save_link(bot, up):
    try:
        FIFO.append(up.message.text) 
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)
    except:
        up.message.reply_text("Something wrong saving the FIFO, but i don't know why..")

    finally:
        up.message.reply_text("New element appended on queue, {} in list".format(len(FIFO)))


def queue(b,u):
    if u.message.chat_id in admin:
        text = "*In attesa di pubblicazione:* _{}_\n\n".format(len(FIFO))

        for item in FIFO:
            text += item + "\n\n"

        u.message.reply_text(text, parse_mode='markdown')


def send_admin(bot, message):
    for a in admin:
        bot.send_message(a, message)


def main():
    updater = Updater("673061913:AAFY6hTOYJDvT-Sp3ohJF5IkqW2oDFS4WuY")
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("q", queue))
    dp.add_handler(MessageHandler(Filters.text, save_link))
    
    # All posting times 
    updater.job_queue.run_daily(send_link, datetime.time(7, 30))
    updater.job_queue.run_daily(send_link, datetime.time(8, 30))
    updater.job_queue.run_daily(send_link, datetime.time(12, 30))
    updater.job_queue.run_daily(send_link, datetime.time(13, 30))
    updater.job_queue.run_daily(send_link, datetime.time(19, 30))
    updater.job_queue.run_daily(send_link, datetime.time(20, 30))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
