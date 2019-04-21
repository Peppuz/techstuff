# techstuff
Codebase for techstuff telegram channel

## Workflow
* start doesn't do nothing, 
* incoming messages which are links, are checked that they are links , and stored in a FIFO queue.
* For every posting_time the bot processes the link, grabs the page's title, format the text to send with title and link and sends it.

