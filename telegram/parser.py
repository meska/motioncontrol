#coding:utf-8
"""
  Author:  Marco Mescalchin --<>
  Purpose: incoming messages parser for telegram bot
  Created: 06/25/15

# commandlist to use with @BotFather
show - Visualizza cams
alerts - Interfaccia Alerts
alert_status - Stato dei tuoi Alerts
pause - Metti in pausa gli Alerts
status - Camera Status
"""
from io import BytesIO
import re
import requests
from django.conf import settings
from django.core.urlresolvers import reverse

EM_MOTION = '\U0001f3c3'
EM_PAUSE = '\U0001f6b6'
EM_ENABLE = '\U0001f514'
EM_DISABLE = '\U0001f515'


class Parser():
    patterns = [
        ['/help','help'],
        ['/show','show'],
        ['/gnocca','boobs'],
        ["(.*)\s+\U0001f4f7",'showcam'],   
        ["/sc(\d+)",'showcam'],
        ["/s_(.*)",'showcam'],
        ["(.*)\s+([%s%s])\s([%s%s])" % (EM_ENABLE,EM_DISABLE,EM_MOTION,EM_PAUSE),'alert'],
        #["(.*)\s+",'alert'],
        ['/alerts','alerts'],
        ['/alert_status','alert_status'],
        ['/alert_onmotion','alert_onmotion'],
        ['/alert_onpause','alert_onpause'],
        ['/pause','pause'],
        ['/status','status'],
        ['/ifttt_single','ifttt_single'],
        ['/ifttt','ifttt'],
        #['/stop','start'],
        #['/start','stop'],
    ]    
    
    
    def __init__(self,bot):
        self.bot = bot
    
    def getUser(self,message):
        # get or create user from db
        from telegrambot.models import TelegramUser
        u,created = TelegramUser.objects.get_or_create(user_id=message['from']['id'])
        save = False

        if 'username' in message['from']:
            if not u.username == message['from']['username']:
                u.username = message['from']['username']
                save =True

        if 'first_name' in message['from']:
            if not u.first_name == message['from']['first_name']:
                u.first_name = message['from']['first_name']
                save =True

        if 'last_name' in message['from']:
            if not u.last_name == message['from']['last_name']:
                u.last_name = message['from']['last_name']
                save =True
        if save:
            u.save()
            
        if created:
            self.bot.sendMessage(u.user_id,"Welcome to MotionBot") #,reply_to_message_id=message['message_id'])
        return u
    
    def split(self,arr, size):
        arrs = []
        while len(arr) > size:
            pice = arr[:size]
            arrs.append(pice)
            arr   = arr[size:]
        arrs.append(arr)
        return arrs    
    
    def ifttt(self,message,chat_id,user):
        # ifttt instructions
        text = "È possibile attivare e disattivare le cam utilizzando ifttt:\n"
        text+= "Su action scegliere l'opzione Maker e impostare un url a scelta tra quelli proposti di seguito, quindi su method selezionare GET, il resto può rimanere vuoto\n\n"

        text+= "Tutti gli avvisi:\n"
        text+= "Attiva:%s%s\n" % (settings.TELEGRAM_WEBHOOK_URL,reverse('motioncontrol.views.ifttthook',args=[user.user_id,'unpause','all'] ))
        text+= "Disattiva: %s%s\n" % (settings.TELEGRAM_WEBHOOK_URL,reverse('motioncontrol.views.ifttthook',args=[user.user_id,'pause','all'] ))
        text+= "\n"
        text+= "Per gli avvisi su singola Cam: digitare /ifttt_single"
            
        
        self.bot.sendMessage(user.user_id,text)

    def ifttt_single(self,message,chat_id,user):
        # ifttt instructions
        from motioncontrol.models import Cam
        text = "Avviso su singola Cam:\n"
        for c in Cam.objects.filter(online=True):
            text+= "Avvisa su movimento  %s:\n%s%s\n" % (c.name,settings.TELEGRAM_WEBHOOK_URL,reverse('motioncontrol.views.ifttthook',args=[user.user_id,'onmotion',c.id] ))
            text+= "Disattiva su movimento  %s:\n%s%s\n" % (c.name,settings.TELEGRAM_WEBHOOK_URL,reverse('motioncontrol.views.ifttthook',args=[user.user_id,'offmotion',c.id] ))
            text+= "Attiva su pausa %s:\n%s%s\n" % (c.name,settings.TELEGRAM_WEBHOOK_URL,reverse('motioncontrol.views.ifttthook',args=[user.user_id,'onpause',c.id] ))
            text+= "Disattiva su pausa %s:\n%s%s\n\n" % (c.name,settings.TELEGRAM_WEBHOOK_URL,reverse('motioncontrol.views.ifttthook',args=[user.user_id,'offpause',c.id] ))
            
        
        self.bot.sendMessage(user.user_id,text)

    def boobs(self,message,chat_id,user):
        # just for fun
        print("want boobs!")
        f = requests.get("http://api.oboobs.ru/noise/1")
        res = f.json()
        boobsurl = 'http://media.oboobs.ru/' + res[0]['preview']
        res = requests.get(boobsurl)
        fp = BytesIO()
        fp.write(res.content)
        fp.seek(0)
        self.bot.sendPhoto(chat_id,fp)

    def butts(self,message,chat_id,user):
        # just for fun
        print("want butts!")
        f = requests.get("http://api.obutts.ru/noise/1")
        res = f.json()
        boobsurl = 'http://media.obutts.ru/' + res[0]['preview']
        res = requests.get(boobsurl)
        fp = BytesIO()
        fp.write(res.content)
        fp.seek(0)
        self.bot.sendPhoto(chat_id,fp)             


    def help(self,message,chat_id,user):
        self.bot.action_typing(chat_id)
        self.bot.sendMessage(chat_id,"TODO: Testo help" ) # ,reply_to_message_id=message['message_id'])
        return        
    
    
    def show(self,message,chat_id,user):
        self.bot.action_typing(chat_id)
        # carica l'elenco delle telecamere
        from motioncontrol.models import Cam
        keys = []
        funcs = []
        for c in Cam.objects.filter(online=True):
            keys.append(u"%s \U0001f4f7" % c.name) 
            #funcs.append('/s_%s' % (c.name.replace(' ','_')))
     
        if keys:
            #self.bot.sendMessage(chat_id,"Seleziona una cam:\n%s" % "\n".join(funcs), reply_markup={'keyboard':self.split(keys,2)}  )# ,reply_to_message_id=message['message_id'])
            self.bot.sendMessage(chat_id,"Seleziona una cam:", reply_markup={'keyboard':self.split(keys,2)}  )# ,reply_to_message_id=message['message_id'])
        else:
            self.bot.sendMessage(chat_id,"Nessuna cam online al momento")# ,reply_to_message_id=message['message_id'])
        
        return        
    
    def alerts(self,message,chat_id,user):
        commands = [
            '/alert_status Stato dei tuoi Alerts',
            '/alert_onpause Attiva alert su fermo',
            '/alert_onmotion Attiva alert su movimento'
        ]
        self.bot.sendMessage(chat_id,"Seleziona un opzione:\n%s" % "\n".join(commands))# ,reply_to_message_id=message['message_id'])
        user.last_message = message
        user.save()             

    def alert_status(self,message,chat_id,user):
        from motioncontrol.models import AlertSubscription
        alerts_sub = AlertSubscription.objects.filter(destination=chat_id,enabled=True)
        alerts = []
        for a in alerts_sub:
            alerts.append(
                "%s: %s %s" % (a.cam.name,"Movimento" if a.alert_motion else 'Fermo','(in pausa)' if a.pause else '')
            )
        
        self.bot.sendMessage(chat_id,"Alerts Attivi:\n%s" % "\n".join(alerts))# ,reply_to_message_id=message['message_id'])
        user.last_message = message
        user.save()          

    def status(self,message,chat_id,user):
        from motioncontrol.models import Cam
        cams = Cam.objects.all()
        online = []
        offline = []
        for c in cams:
            if c.online:
                online.append(c.name)
            else:
                offline.append(c.name)
        
        self.bot.sendMessage(chat_id,"Sato Cams:\n\nOnline:\n%s\n\nOffline:\n%s" % ("\n".join(online),"\n".join(offline)))# ,reply_to_message_id=message['message_id'])
        user.last_message = message
        user.save()  
        
    def pause(self,message,chat_id,user):
        from motioncontrol.models import AlertSubscription
        alerts_sub = AlertSubscription.objects.filter(destination=chat_id,enabled=True)

        pause = None
        for a in alerts_sub:
            if pause == None:
                # the first rule the others
                pause = False if a.pause else True

            a.pause = pause
            a.save()
        
        self.alert_status(message, chat_id, user)


    def alert_onmotion(self,message,chat_id,user):
        self.bot.action_typing(chat_id)
        # carica l'elenco delle telecamere
        from motioncontrol.models import Cam,AlertSubscription

        
        keys = []
        for c in Cam.objects.filter(online=True):
            if c.name:
                alert,created = AlertSubscription.objects.get_or_create(
                    channel = 'telegram',
                    destination = chat_id,
                    cam = c,
                    alert_motion = True,
                    alert_nomotion = False,
                )
                if alert.enabled:
                    keys.append("%s %s %s" % (c.name,EM_DISABLE,EM_MOTION) )
                else:
                    keys.append("%s %s %s" % (c.name,EM_ENABLE,EM_MOTION) )
                    
        self.bot.sendMessage(chat_id,"Attiva / Disattiva Alert su movimento?",reply_markup={'keyboard':self.split(keys,2)} )# ,reply_to_message_id=message['message_id'])
        user.last_message = message
        user.save()            
        
        return         
    
    def alert_onpause(self,message,chat_id,user):
        self.bot.action_typing(chat_id)
        # carica l'elenco delle telecamere
        from motioncontrol.models import Cam,AlertSubscription

        
        keys = []
        for c in Cam.objects.filter(online=True):
            if c.name:
                alert,created = AlertSubscription.objects.get_or_create(
                    channel = 'telegram',
                    destination = chat_id,
                    cam = c,
                    alert_motion = False,
                    alert_nomotion = True,
                )
                if alert.enabled:
                    keys.append("%s %s %s" % (c.name,EM_DISABLE,EM_PAUSE) )
                else:
                    keys.append("%s %s %s" % (c.name,EM_ENABLE,EM_PAUSE) )
                    
        self.bot.sendMessage(chat_id,"Attiva / Disattiva Alert su pausa?",reply_markup={'keyboard':self.split(keys,2)} )# ,reply_to_message_id=message['message_id'])
        user.last_message = message
        user.save()            
        
        return     
    
    def alert(self,message,chat_id,user,args):
        # enable disable alerts
        from motioncontrol.models import Cam,AlertSubscription
        self.bot.action_typing(chat_id)

        c = Cam.objects.get(name=args[0])
        alert,created = AlertSubscription.objects.get_or_create(
            channel = 'telegram',
            destination = chat_id,
            cam = c,
            alert_motion = True if args[2] == EM_MOTION else False,
            alert_nomotion = True if args[2] == EM_PAUSE else False,
        )
        alert.enabled = True if args[1] == EM_ENABLE else False
        if alert.enabled:
            self.bot.sendMessage( user.user_id,"Alert su %s attivato per %s" % ( "movimento" if args[2] == EM_MOTION else "pausa",args[0]) ,reply_markup={'hide_keyboard':True} )
        else:
            self.bot.sendMessage( user.user_id,"Alerts su %s disattivato per %s" % ("movimento" if args[2] == EM_MOTION else "pausa",args[0]) ,reply_markup={'hide_keyboard':True} )

        alert.save()
            
    
    
    def showcam(self,message,chat_id,user,args):
        # mostro la telecamera scelta
        from motioncontrol.models import Cam
        self.bot.action_typing(chat_id)
        try:
            if args[0].isdecimal():
                c = Cam.objects.get(id=int(args[0]))
            else:
                c = Cam.objects.get(name=args[0].replace('_',' '))
            fp = BytesIO()
            c.snapshot().save(fp,'JPEG')
            fp.seek(0)
            self.bot.sendPhoto(user.user_id,fp,reply_markup={'hide_keyboard':True})
            #self.bot.sendMessage(user.user_id,"Live stream: %s%02d" % (c.server.stream_url,c.thread_number))
            
        except Exception as e:
            self.bot.sendMessage( user.user_id,"Error Retrieving Snapshot from %s" % args[0] ,reply_markup={'hide_keyboard':True} )

    
    def parse(self,message):
        user = self.getUser(message)
        text = message['text']

        
        # find method
        for c in self.patterns:
            m = re.match(c[0],text)
            if m:
                if m.groups():
                    getattr(self,c[1])(text,user.user_id,user,m.groups())
                else:
                    getattr(self,c[1])(text,user.user_id,user)
                return True
                

        # defaults
        return True
        # discard
        #self.bot.sendMessage(user.user_id,"",reply_to_message_id=message['message_id'],reply_markup={'hide_keyboard':True})