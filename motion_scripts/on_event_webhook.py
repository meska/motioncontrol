#!/usr/bin/env python
#coding:utf-8
"""
  Author: Marco Mescalchin --<>
  Purpose: Motion, on_picture_save Script
  Created: 06/24/15
"""
import os,sys,requests,json
WEBHOOK = 'http://cam.mecomsrl.com/mc/webhook/'

try:
    # call webhook
    r = requests.post(WEBHOOK,data=json.dumps(sys.argv),timeout=10)
except:
    pass


