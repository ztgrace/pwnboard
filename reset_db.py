#!/usr/bin/env python3

import redis
r = redis.StrictRedis(host='localhost')
r.flushdb()
