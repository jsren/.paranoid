#!/usr/bin/python
#
# paranoid_daemon.py - (c) 2016 James S Renwick
# ---------------------------------------------
# Authors: James S Renwick

import re
import os
import json
import time
import subprocess
import threading
import SocketServer

HOST = "localhost"
PORT = 9475


users = dict()
this_username = subprocess.check_output(['whoami']).strip()

notifications_enabled = True

# Matches: "s1343880  Naohiro Kakimura  pts/1 2  Nov 16 03:31 (sampras.inf.ed.ac.uk)"
user_regex = re.compile(r"^(\w+)\s+((?:(?:\w)|(?:\s\S))+)\s+(?:\S+)\s+(?:\d+)?\s+" + \
    r"((?:\w+)\s(?:\d+)\s(?:\d+):(?:\d+))(?:[^\(]+)\(([^\)]*)\)\s*$")


class User(object):
    def __init__(self, username, full_name, login_time, hostname):
        self.username   = username
        self.full_name  = full_name
        self.login_time = login_time
        self.hostname   = hostname

    def to_dict(self):
        return { v: getattr(self, v) for v in vars(self) if not v.startswith('_') }


class CancellationToken(object):
    def __init__(self, cancelled=False):
        self.__cancelled = False

    def cancel(self):
        self.__cancelled = True

    def cancelled(self):
        return self.__cancelled


def update():
    try:
        user_lines = [l.strip() for l in subprocess.check_output(['finger']).split('\n') if l]
    except Exception as e:
        print "[ERROR] Exception running finger: %s" % e
        return
    else:
        users.clear()

    for line in user_lines:
        # Match 'finger' output row
        user_match = user_regex.match(line)
        if not user_match: continue

        # Parse & add the user entry
        user = User(user_match.group(1).strip(), user_match.group(2).strip(), \
            user_match.group(3).strip(), user_match.group(4).strip())
        users[user.username] = user



def notify_user_login(user, compat=False):
    try:
        message = "%s (%s) logged in from '%s'"%(user.full_name, user.username, user.hostname)
        if not compat:
            os.system('notify-send -u critical "User Logged In" "' + message + '"')
        else:
            os.system('xmessage "' + message + '"')
    except:
        if not compat:
            os.system('notify-send -u critical "<unknown> User Logged In"')
        else:
            os.system('xmessage "<unknown> User Logged In"')


def notify_user_logoff(user, compat=False):
    try:
        message = "%s (%s) logged off from '%s'"%(user.full_name, user.username, user.hostname)
        if not compat:
            os.system('notify-send -u critical "User Logged Off" "' + message + '"')
        else:
            os.system('xmessage "' + message + '"')
    except:
        if not compat:
            os.system('notify-send -u critical "<unknown> User Logged Off"')
        else:
            os.system('xmessage "<unknown> User Logged Off"')


def daemon(cancellation_token, refresh_rate=2000, compat=False):
    update()
    known_users = dict(users)

    while not cancellation_token.cancelled():
        update()
        latest_users = dict(users)

        if notifications_enabled:
            for user in known_users.itervalues():
                if user.username not in latest_users:
                    notify_user_logoff(user, compat=compat)
            for user in latest_users.itervalues():
                if user.username not in known_users:
                    notify_user_login(user, compat=compat)

        known_users = latest_users
        time.sleep(refresh_rate/1000.0)



class RequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Get request
        request = self.request.recv(1024).strip()
        if not request: return

        global notifications_enabled

        # Parse request
        try:
            request = json.loads(request)
            action = request['action']
        except Exception as e:
            response = json.dumps(dict(code=1, error_msg=str(e)))
        else:
            # Handle request
            try:
                if action == "get-this-user":
                    if not users.has_key(this_username):
                        response = json.dumps(dict(code=2, error_msg="Cannot 'finger' current user."))
                    else:
                        output = dict(code=0, value=users[this_username].to_dict())
                        response = json.dumps(output)
                elif action == "get-all-users":
                    output = dict(code=0, value=[users[u].to_dict() for u in users])
                    response = json.dumps(output)
                elif action == "get-other-users":
                    output = dict(code=0, value=[users[u].to_dict() for u in users if u != this_username])
                    response = json.dumps(output)
                elif action == "shutdown":
                    threading.Thread(target=self.shutdown).start()
                    return
                elif action == "silence":
                    notifications_enabled = False
                    response = json.dumps(dict(code=0))
                elif action == "notify":
                    notifications_enabled = True
                    response = json.dumps(dict(code=0))
                else:
                    raise RuntimeError("Unknown action '%s'."%action)
            except Exception as e:
                response = json.dumps(dict(code=2, error_msg=str(e)))
        
        self.request.sendall(response)

    def shutdown(self):
        print "[INFO ] Shutting down..."
        self.server.shutdown()
        print "[INFO ] Shut down."



if __name__ == "__main__":
    # Start user daemon
    ct = CancellationToken()
    daemon_thread = threading.Thread(target=daemon, args=(ct,))
    daemon_thread.start()

    # Start command server
    server = SocketServer.TCPServer((HOST, PORT), RequestHandler)
    server.serve_forever()

    # Once server finished, cancel daemon and close
    ct.cancel()
    server.server_close()
    del server
