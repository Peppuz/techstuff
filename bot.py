import requests
import logging
import os
import json
import telegram
import time
import datetime
from lxml.html import fromstring
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


admin = [135605474, 311495487] # 311495487 
channel_id = -1001261875848
FIFO = []
PRODUCTION = False

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
    l.exception("Queue file not found, creating a new file")
    with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)


def get_title(link):
    text = None
    try:
        r = requests.get(link)
        title = fromstring(r.content).findtext('.//title')
        title = "*"+title+"*"
        
    except requests.exceptions.InvalidSchema:
        up.message.reply_text("Link errato o non schema invalido!")
        l.exception("Link not valid, Invalid Schema, link: {}".format(link))

    except IOError as e:
        send_admin(bot, str(e))
        l.exception("SocketError:" )
        
    except UnicodeEncodeError as e: 
        send_admin(bot, str(e))
        l.exception("Unicode Error: re-encoding in utf-8")

        if text in FIFO:
            l.warning("Link gia presente nella coda FIFO")
            return False


    except Exception as e:
        up.message.reply_text(str(e))
        l.exception("General.exception, link: {}".format(link))

    finally:
        text = u'\n'.join((title, link)).encode('utf-8').strip()

    l.info("Get info: {}".format(text)) 
    return text


def start(bot, update):
    update.message.reply_text('Hi!')


def send_link(bot, job):
    try:
        l.info("It's time to send the link, starting...")
        text = FIFO.pop(0)
        bot.send_message(channel_id, text=text, parse_mode="markdown")
        
        # Monitoring
        send_admin(bot, "Link postato, link in queue: %s" % len(FIFO))
        if len(FIFO) == 1:
            send_admin(bot, "1 Articolo rimane da pubblicare, aggiungine altri!")

    except IndexError as e:
        l.exception('Exception Index Error: {}'.format(e))
        send_admin(bot, "Lista vuota!!")

    except Exception as e:
        l.exception('General Exception: {}'.format(e))
        send_admin(bot, str(e))

    finally: 
        json.dump(FIFO, open('fifo.json', 'w'))


def save_link(bot, up):
    text = None
    try:
        link = up.message.text
        l.info("New message incoming, handled as link {}".format(link))
        text = get_title(link)
        if text in FIFO:
            l.warning("Link gia presente nella coda FIFO")
            up.message.reply_text("Questo link esiste gia nella FIFO!")
            return False

        l.info("Appending link on Queue")
        FIFO.append(text)
        up.message.reply_text("New element appended on queue, {} in list".format(len(FIFO)))

    except requests.exceptions.InvalidSchema:
        up.message.reply_text("Link errato o non schema invalido!")
        l.exception("Link not valid, Invalid Schema, link: {}".format(link))

    except IOError as e:
        send_admin(bot, str(e))
        l.exception("SocketError")
        
    except Exception as e:
        up.message.reply_text(str(e))
        err = "General.exception, link: {}\n\n{}".format(link, str(e))
        l.exception(err)
        bot.send_message(135605474, err)

    finally:
        l.info("Saving Queue")
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)


def move(b,u): 
    text = u.message.text
    text = text.split(' ')
    command = text[0]
    index = text[1]
    testo = text[2:]
   
    if u.message.chat_id in admin:
        try: 
            item = FIFO[int(index)]
            item = item.split('\n')
            title  = u' '.join(testo)
            title = u'*'+title+u'*'

            new_item = u'\n'.join((title, item[1])).encode('utf-8').strip()
            FIFO[int(index)] = new_item 
            send_admin(b, "Element Renamed! check it /q")
        except Exception as e:
            l.exception('Rename Chat')
            send_admin(b, "Element not Renamed!\nCheck logs ")
        finally:
            l.info("Saving Queue")
            with open('fifo.json', 'w') as ff:
                json.dump(FIFO, ff)
        

def queue(b,u):
    if u.message.chat_id in admin:
        text = u"*In attesa di publicazione:* _{}_\n\n".format(len(FIFO))
        counter = 0
        for item in FIFO:
            text += u"%s. %s \n\n" % (str(counter), item)
            counter += 1 

        b.send_message(u.message.chat_id, text.encode('utf-8'), parse_mode='markdown')


def remove(b, u):
    try:
        num = int(u.message.text[4:]) 
        removed = FIFO.pop(num) 
        l.info("Removed link {} - {} - from Queue".format(num, removed))
        u.message.reply_text("Elemento rimosso dalla lista")

    except:
        l.exception("Failed removing from fifo")
        u.message.reply_text("Non ci sono elementi a questa posizione nella lista")

    finally:
        l.info("Saving Queue")
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)
        

def send_admin(bot, message):
    for a in admin:
        bot.send_message(a, message, parse_mode='markdown')


def insert(bot, message):
    data = message.message.text.split(' ')
    index = int(data[1])
    link = int(data[2])
    
    try:
        l.info("Insert incoming, handled as link {}".format(link))
        text = get_title(link)
        l.info("Text formatted: {}".format(text))
        if text in FIFO:
            l.warning("Link gia presente nella coda FIFO")
            up.message.reply_text("Questo link esiste gia nella FIFO!")
            return False

        l.info("Appending link on Queue")
        FIFO.insert(index, text)
        message.message.reply_text("New element appended on queue, {} in list".format(len(FIFO)))
        
    except Exception as e:
        send_admin(bot, str(e))
        l.exception("General.exception, link: {}".format(link))

    finally:
        l.info("Saving Queue")
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)

    return True 


def weekend_reminder(b, u): 
    send_admin("*IT'S WEEKEND BITCH*\nOrari: 9 - 15 - 21")


def main():
    token ="673061913:AAHjaEPvX4M4x1NYE5MrXgsJ9eSRu8yQj3c"
    updater = Updater(token)
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("q", queue))
    dp.add_handler(CommandHandler("rm", remove))
    dp.add_handler(CommandHandler("mv", move))
    dp.add_handler(CommandHandler("i", insert))
    dp.add_handler(CommandHandler('p', send_link))
    dp.add_handler(CommandHandler("on", lambda bot, mess: send_admin(bot, "Bot up and running...")))
    dp.add_handler(CommandHandler("say", lambda bot, mess: send_admin(bot, mess.message.text[4:])))

    dp.add_handler(MessageHandler(Filters.text, save_link))
    
    
    # UNCOMMENT WHEN DEBUGGING
    #updater.job_queue.run_daily(send_link, datetime.datetime.today())
    #channel_id = -1001480479440
    dp.add_handler(CommandHandler('p', send_link))
    dp.add_handler(CommandHandler("on", lambda bot, mess: send_admin(bot, "Bot up and running...")))
    
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
    # Reminder Weekend
    updater.job_queue.run_daily(weekend_reminder, datetime.time(9, 0), days=(5,6))


    
    # Handle Errors
    # dp.add_handler(error) 

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
