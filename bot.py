import requests, logging, os, json, telegram, time, datetime
from airtable import airtable
from lxml.html import fromstring
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

admin = [135605474, 311495487] # 311495487 
channel_id = -1001261875848
at = airtable.Airtable('app0H4qDbdjTXfmfB', 'keyom1R0JvwYZgXju')

logging.basicConfig(
        filename='techstuff.log',
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s:  %(message)s')
l = logging.getLogger(__name__)


def get_title(bot, link):
    """ Given a single link gets the title 
        and returns the title and source in markdown (NOT THE LINK)
    """
    text = None
    try:
        r = requests.get(link)
        title = fromstring(r.content).findtext('.//title')
        title = title.split('-') 
        if len(title) == 1:
            title = title[0].split('|')
        source = title[-1]
        text = u"*{}* - {}".format(title[0], source)
        print(text)
        
    except requests.exceptions.InvalidSchema:
        send_admin(bot, "Link errato o non schema invalido!")
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
        send_admin(bot, str(e))
        l.exception("General.exception, link: {}".format(link))


    l.info("Get info: {}".format(text)) 
    return text


def start(bot, update):
    update.message.reply_text('Hi!')


def send_link(bot, job):
    """ Gets from airtable the first element in position, publishes and removes the record """
    try:
        l.info("It's time to send the link, starting...")
        post = at.get('techstuff')['records'][0]
        
        text = "{} \n{}".format(post['fields']['Title'],post['fields']['Link'])
        bot.send_message(channel_id, text=text, parse_mode="markdown")
        
        ll= len(at.get('techstuff')['records'])
        send_admin(bot, "Link postato, link in queue: %s" % ll)
        at.delete('techstuff', post['id'])

    except Exception as e:
        l.exception('General Exception: {}'.format(e))
        send_admin(bot, str(e))


def save_link(bot, up):
    """ Incoming Links get saved to airtable, after beign processed. """ 
    text = None
    al = at.get('techstuff')
    links = []
    for a in al['records']:
        links.append(a['fields']['Link'])

    try:
        link = up.message.text
        l.info("New message incoming, handled as link {}".format(link))
        text = get_title(bot, link)
        if text is None:
            send_admin(bot, "E' stato rilevato un errore nel titolo del Link. text == None")
            l.warning("E' stato rilevato un errore nel titolo del Link. text == None")
            return False
        if link in links:
            l.warning("Link gia presente nella coda FIFO")
            send_admin(bot, "Questo link esiste gia nella FIFO!")
            return False

        l.info("Appending link on Queue")
        at.create('techstuff', {"Title":text, "Link":link })
        up.message.reply_text("New element appended on queue, {} in list".format(len(FIFO)))

    except requests.exceptions.InvalidSchema:
        send_admin(bot, "Link errato o non schema invalido!")
        l.exception("Link not valid, Invalid Schema, link: {}".format(link))

    except IOError as e:
        send_admin(bot, str(e))
        l.exception("SocketError")

    except Exception as e:
        err = "General.exception, link: {}\n\n{}".format(link, str(e))
        l.exception(err)
        bot.send_message(135605474, err)


def move(b,u): 
    """ Rename or move to Position a Record 
        ES. /mv 2 Text chat shish 
    """ 
    return

    text = u.message.text
    text = text.split(' ')
    command = text[0]
    index = text[1]
    testo = text[2:]
   
    if u.message.chat_id in admin:
        try: 
            item = FIFO[int(index)]
            i = item.split('\n')
            title  = u' '.join(testo)

            print(title, i) 
            new_item = u'\n'.join((title, i[1])).encode('utf-8').strip()
            FIFO[int(index)] = new_item 
            send_admin(b, "Element Renamed! check it /q")
        except Exception as e:
            l.exception('Rename Chat')
            send_admin(b, "Element not Renamed!\nERROR:\'n{}".format(str(e)))
        finally:
            l.info("Saving Queue")
            with open('fifo.json', 'w') as ff:
                json.dump(FIFO, ff)
        

def queue(b,u):
    ''' Sends the whole queue '''
    if u.message.chat_id in admin:
        coddio = at.get('techstuff')['records']
        text = u"*In attesa di publicazione:* _{}_\n\n".format(len(coddio))
        for item in at.get('techstuff')['records']:
            text += u"%s. %s \n\n" % (item['fields']['Index'], item['fields']['Title'])
        b.send_message(u.message.chat_id, text.encode('utf-8'), parse_mode='markdown')


def remove(b, u):
    ''' Remove element from airtable
        ES. /rm 4
    '''
    try:
        num = int(u.message.text[4:]) 
        record = at.get('techstuff', filter_by_formula="Index = '{}'".format(num))
        u.message.reply_text("Elemento {}".format(record[0]['fields']['Title']))
        at.delete('techstuff', record['records'][0]['id'])
        l.info("Removed link {} - from Queue".format(num))
        u.message.reply_text("Elemento rimosso dalla lista")

    except:
        l.exception("Failed removing from fifo")
        u.message.reply_text("Non ci sono elementi a questa posizione nella lista")


def send_admin(bot, message):
    for a in admin:
        bot.send_message(a, message)


def insert(bot, message):
    """ TODO """
    return 

    data = message.message.text.split(' ')
    index = int(data[1])
    link = int(data[2])
    
    try:
        l.info("Insert incoming, handled as link {}".format(link))
        text = get_title(bot, link)
        l.info("Text formatted: {}".format(text) )

        if link in [a['fields']['Link'] for a in at.get('techstuff')['records']]:
            l.warning("Link gia presente nella coda FIFO")
            send_admin(bot, "Questo link esiste gia nella FIFO!")
            return False

        l.info("Appending link on Queue")
        at.create('techstuff', {"Link": link, "Title":text, "Index":index})
        l.info("Link on Queue added")
        send_admin(bot, "New element appended on queue /q")
        
    except Exception as e:
        send_admin(bot, str(e))
        l.exception("General.exception, link: {}".format(link))

    finally:
        l.info("Saving Queue")
        with open('fifo.json', 'w') as ff:
            json.dump(FIFO, ff)

    return True 


def main():
    token ="673061913:AAHjaEPvX4M4x1NYE5MrXgsJ9eSRu8yQj3c"
    updater = Updater(token, use_context=True)
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
    
    # days
    updater.job_queue.run_daily(send_link, datetime.time(9, 0), days=(0,1,2,3,4,5,6))
    updater.job_queue.run_daily(send_link, datetime.time(15, 0), days=(0,1,2,3,4,5,6))
    updater.job_queue.run_daily(send_link, datetime.time(21, 0), days=(0,1,2,3,4,5,6))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
