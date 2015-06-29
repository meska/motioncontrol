#!/usr/bin/env python
#coding:utf-8
"""
  Author: Marco Mescalchin --<>
  Purpose: Motion, on event Script Redis version
  Created: 06/24/15
"""
import os,sys,redis,json

MOTION_REDIS_SERVER = 'cartman.mecom.lan'
r = redis.StrictRedis(host=MOTION_REDIS_SERVER, port=6379, db=0)
r.rpush('motion-event',json.dumps(sys.argv))
