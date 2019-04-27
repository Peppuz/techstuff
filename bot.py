import requests
import logging
import json
import telegram
import time
import datetime
from lxml.html import fromstring
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


admin = [135605474, 311495487] # 311495487 
channel_id = -1001261875848
FIFO = []

logging.basicConfig(level=logging.INFO)
logging.config.fileConfig('logging.ini')
l = logging.getLogger(__name__)


try:
    with open('fifo.json') as ff:
            FIFO = json.load(ff)
            l.info("[INFO] Queue loaded correctly")

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

        if title == None:
            title = ""
        # Formatting text
        text = "*{}* \n {}".format(title, link)
        bot.send_message(channel_id, text=text, parse_mode="markdown")
        
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
        link = up.message.text
        r = requests.get(link)
        if link in FIFO:
            up.message.reply_text("Questo link esiste gia nella FIFO!")
            return
        FIFO.append(link)
        up.message.reply_text("New element appended on queue, {} in list".format(len(FIFO)))
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)

    except requests.exceptions.InvalidSchema:
        up.message.reply_text("Link non valido, correggi e reinvia.")

    except Exception as e:
        up.message.reply_text("Something wrong saving the FIFO, but i don't know why..")
        raise e


def queue(b,u):
    if u.message.chat_id in admin:
        text = "*In attesa di pubblicazione:* _{}_\n\n".format(len(FIFO))
        counter = 0
        for item in FIFO:
            text += "{}. {} \n\n".format(str(counter), item)
            counter += 1 
        u.message.reply_text(text, parse_mode='markdown')


def remove(b, u):
    try:
        num = int(u.message.text[4:]) 
        removed = FIFO.pop(num) 
        u.message.reply_text("Elemento rimosso dalla lista")

    except:
        u.message.reply_text("Non ci sono elementi a questa posizione nella lista")

    finally:
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)
        

def send_admin(bot, message):
    for a in admin:
        bot.send_message(a, message)


def main():
    updater = Updater("673061913:AAFY6hTOYJDvT-Sp3ohJF5IkqW2oDFS4WuY")
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("q", queue))
    dp.add_handler(CommandHandler("rm", remove))
    dp.add_handler(MessageHandler(Filters.text, save_link))
    
    # week days posting times 
    updater.job_queue.run_daily(send_link, datetime.time(7, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(8, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(12, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(13, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(19, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(20, 30), days=(0,1,2,3,4))

    # Weekend days
    updater.job_queue.run_daily(send_link, datetime.time(9, 0), days=(5,6))
    updater.job_queue.run_daily(send_link, datetime.time(15, 0), days=(5,6))
    updater.job_queue.run_daily(send_link, datetime.time(21, 0), days=(5,6))


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
