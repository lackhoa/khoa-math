import sched, time
import urllib.request
import multiprocessing as mp
import signal
import os

sites = [
    'https://www.yahoo.com/',
    'http://www.cnn.com',
    'http://www.python.org',
    'http://www.jython.org',
    'http://www.pypy.org',
    'http://www.perl.org',
    'http://www.cisco.com',
    'http://www.facebook.com',
    'http://www.twitter.com',
    'http://www.macrumors.com/',
    'http://arstechnica.com/',
    'http://www.reuters.com/',
    'http://abcnews.go.com/',
    'http://www.cnbc.com/',
    'http://www.cnbc.com/',
]

def sitesize(url):
    ''' Determine the size of a website '''
    with urllib.request.urlopen(url) as u:
        page = u.read()
        return url, len(page)

def multi_sitesize(urls):
    for url in urls:
        print(sitesize(url))

def stop(proc):
    os.kill(proc.pid, signal.SIGSTOP)
    print('Pausing process of pid {}'.format(proc.pid))
    import time; time.sleep(2)
    print('Resuming now')
    os.kill(proc.pid, signal.SIGCONT)

s = sched.scheduler(time.time, time.sleep)
p = mp.Process(target=multi_sitesize, args=(sites,))
s.enter(3, 1, stop, argument=(p,))  # pause the process `p` after 3 seconds
p.start()
s.run()
