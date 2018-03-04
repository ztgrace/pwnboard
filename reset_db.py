#!/usr/bin/env python

import redis
r = redis.StrictRedis(host='localhost')
r.flushdb()
