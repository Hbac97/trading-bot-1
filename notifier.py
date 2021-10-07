import discord_notify as dn
import config

class Notifier():
    def __init__(self):
        self.notifier = dn.Notifier(config.DISCORD_NOTIFY_WEBHOOK_URL)

    def notify(self,msg):
        try:
            notifier.send(msg)
        except:
            pass