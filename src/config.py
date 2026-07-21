DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
PK_REFRESH_INTERVAL = 0.05 # seconds between status refresh during PK
RULES = '''\
PK Rules:
  1. Each round, Proxy and Direct send one request to the same URL simultaneously.
  2. The side with lower latency wins the round. (-1 = Failed, counts as loss)
  3. If both fail, it is a tie.
  4. If latencies are exactly equal, it is a tie.
  5. Final score = rounds won. Higher score wins the PK.
'''
