#!/usr/bin/env python
#coding:utf-8
"""
  Author: Marco Mescalchin --<>
  Purpose: Motion, on_picture_save Script
  Created: 06/24/15
"""
import os,sys,requests,json,redis
WEBHOOK = 'http://cam.mecomsrl.com/mc/webhook/'
REDIS_SERVER = 'cartman.mecom.lan'


if sys.argv[1] == 'picture':
    try:
        r = requests.post(WEBHOOK,data=json.dumps(sys.argv),timeout=10)
    except:
        pass

if sys.argv[1] == 'motion':
    r = redis.StrictRedis(host=REDIS_SERVER, port=6379, db=0)
    r.setex('motion-event-%s' % sys.argv[2],30,json.dumps(sys.argv))

#if sys.argv[1] == 'picture-redis':
#    r = redis.StrictRedis(host=REDIS_SERVER, port=6379, db=0)
#    r.set('motion-moving-%s'%sys.arg[1], True, ex=60)
#    r.set('motion-event',json.dumps(sys.argv))

