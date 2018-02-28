# Parser for http://serienplakate.de/

[serienplakate](http://serienplakate.de/) provides free limited posters for every new Netflix show.
This script based on [requests-html](https://github.com/kennethreitz/requests-html) parses website and notifies me via [Telegram](https://core.telegram.org/) if there are posters available to order.

You have to provide several environment variables to be able to run this:

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_USER_ID=...
```
