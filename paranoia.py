#!/usr/bin/python

#!/usr/bin/python
#
# paranoid_daemon.py - (c) 2016 James S Renwick
# ---------------------------------------------
# Authors: James S Renwick


import sys
import json
import socket

ACTION_GET_THIS_USER   = "get-this-user"
ACTION_GET_ALL_USERS   = "get-all-users"
ACTION_GET_OTHER_USERS = "get-other-users"
ACTION_SILENCE         = "silence"
ACTION_NOTIFY          = "notify"
ACTION_SHUTDOWN        = "shutdown"


HOST = "localhost"
PORT = 9475

def print_help():
    print "Help: TODO"


class ParanoiaClient(object):
    def __init__(self, host=HOST, port=PORT):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def __delete__(self):
        self._socket.shutdown(socket.SHUT_RDWR)

    def _send(self, action, **kwargs):
        self._socket.send(json.dumps(dict(action=action, **kwargs)))

    def _send_recv(self, action, **kwargs):
        self._socket.send(json.dumps(dict(action=action, **kwargs)))
        return self._socket.recv(4096).strip()

    def get_this_user(self):
        return self._send_recv(ACTION_GET_THIS_USER)

    def get_all_users(self):
        return self._send_recv(ACTION_GET_ALL_USERS)

    def get_other_users(self):
        return self._send_recv(ACTION_GET_OTHER_USERS)

    def shutdown_server(self):
        return self._send(ACTION_SHUTDOWN)

    def silence_notifications(self):
        return self._send(ACTION_SILENCE)

    def enable_notifications(self):
        return self._send(ACTION_NOTIFY)


def print_user(user):
    print """
username  : %s
full name : %s
login time: %s
hostname  : %s
""" % (user['username'], user['full_name'], \
        user['login_time'], user['hostname']) 

def print_error(code, msg=""):
    print "[ERROR] Error %s: %s"%(code, msg)
    exit(code)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 0:
        print_help()
        exit(0)
    
    client = ParanoiaClient()

    arg_string = " ".join(args).strip().lower()

    if arg_string == "get me":
        response = json.loads(client.get_this_user())
        if response['code'] == 0:
            print_user(response['value'])
        else:
            print_error(response['code'], response.get('error_msg',""))
        
    elif arg_string == "get users" or arg_string == "get all":
        response = json.loads(client.get_all_users())
        if response['code'] == 0:
            for user in response['value']:
                print_user(user)
        else:
            print_error(response['code'], response.get('error_msg',""))
        
    elif arg_string == "get others":
        response = json.loads(client.get_other_users())
        if response['code'] == 0:
            for user in response['value']:
                print_user(user)
        else:
            print_error(response['code'], response.get('error_msg',""))

    elif arg_string == "silence":
        client.silence_notifications()

    elif arg_string == "notify":
        client.enable_notifications()

    elif arg_string == "shutdown":
        client.shutdown_server()
    
    else:
        print_help()
        exit(1)
