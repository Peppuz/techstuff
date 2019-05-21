# techstuff
Codebase for techstuff telegram channel

## Workflow
* `/start`: doesn't do anything. 
* `MessageHandler`: messages are handled as links, get checked and title grab from HTML, than stored in a FIFO queue (local json file)
* `JobHandler`: For each posting_time the first element on fifo get, format the text to send with title and link and sends it.
* `/mv` , `/i`, `/rm` to describe.
