import requests
import logging
import json
import telegram
import time
import datetime
from lxml.html import fromstring
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


admin = [135605474, 311495487] # 311495487 
channel_id = -1001480479440
FIFO = []

logging.basicConfig(
        filename='techstuff.log',
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s:  %(message)s')
       

l = logging.getLogger(__name__)
try:
    with open('fifo.json') as ff:
        l.info("Opening Queue file")
        FIFO = json.load(ff)
        l.info("Queue loaded correctly")

except:
    l.error("Queue file not found, creating a new file")
    with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)


def start(bot, update):
    update.message.reply_text('Hi!')


def send_link(bot, job):
    try:
        l.info("It's time to send the link, starting...")
        link = FIFO.pop(0)
        l.info("Getting link's title")
        r = requests.get(link)
        tree = fromstring(r.content)
        title = tree.findtext('.//title')

        if title == None:
            title = ""

        l.info("Title Result: {}".format(title))
        # Formatting text
        text = "*{}* \n {}".format(title, link)
        l.info("Sending message to channel")
        bot.send_message(channel_id, text=text, parse_mode="markdown")
        
        # Monitoring
        send_admin(bot, "Link postato, link in queue: %s" % len(FIFO))
        if len(FIFO) == 1:
            send_admin(bot, "1 Articolo rimane da pubblicare, aggiungine altri!")

    except IndexError as e:
        send_admin(bot, "Lista vuota!!")

    except requests.exceptions.InvalidSchema as e:
        l.error('Exception Invalid Schema: {}'.format(e))
        send_admin(bot, "Link non valido")

    except Exception as e:
        l.error('General Exception: {}'.format(e))
        send_admin(bot, str(e))

    finally: 
        json.dump(FIFO, open('fifo.json', 'w'))


def save_link(bot, up):
    try:
        l.info("New message incoming, handled as link")
        link = up.message.text
        r = requests.get(link)

        if link in FIFO:
            l.warning("Link gia presente nella coda FIFO")
            up.message.reply_text("Questo link esiste gia nella FIFO!")
            return
        

        l.info("Appending link on Queue")
        FIFO.append(link)
        up.message.reply_text("New element appended on queue, {} in list".format(len(FIFO)))

    except requests.exceptions.InvalidSchema:
        l.error("Link not valid, Invalid Schema, link: {}".format(link), exec_inf=True)

    except Exception as e:
        l.error("Cannot save link, general error, link: {}".format(link), exec_inf=True)
        raise e

    finally:
        l.info("Saving Queue")
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)


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
        l.info("Removed link {} - {} - from Queue".format(num, removed))
        u.message.reply_text("Elemento rimosso dalla lista")

    except:
        l.error("Failed removing from fifo")
        u.message.reply_text("Non ci sono elementi a questa posizione nella lista")

    finally:
        l.info("Saving Queue")
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)
        

def send_admin(bot, message):
    for a in admin:
        bot.send_message(a, message)


def main():
    token ="673061913:AAFY6hTOYJDvT-Sp3ohJF5IkqW2oDFS4WuY"
    updater = Updater(token)
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("q", queue))
    dp.add_handler(CommandHandler("rm", remove))
    dp.add_handler(CommandHandler("on", lambda bot, mess: send_admin(bot, "Bot up and running...")))
    dp.add_handler(MessageHandler(Filters.text, save_link))
    
    # week days posting times 
    updater.job_queue.run_daily(send_link, datetime.time(8, 00), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(9, 00), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(12, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(13, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(19, 30), days=(0,1,2,3,4))
    updater.job_queue.run_daily(send_link, datetime.time(20, 30), days=(0,1,2,3,4))

    # Weekend days
    updater.job_queue.run_daily(send_link, datetime.time(9, 0), days=(5,6))
    updater.job_queue.run_daily(send_link, datetime.time(15, 0), days=(5,6))
    updater.job_queue.run_daily(send_link, datetime.time(21, 0), days=(5,6))


    
    testo ="Starting the service: \nToken: {}\nQueue lenght: {}".format(token, len(FIFO))
    l.info(testo)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
