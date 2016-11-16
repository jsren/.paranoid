![alt tag](https://raw.githubusercontent.com/jsren/.paranoid/master/user_logged_in.png)

## What's in the box ##
1x   Daemon sending gnome notications for other users logging (ssh-ing) in/out

1x   API server for querying current users

1x   Command-line client for controlling the daemon (silencing notifications, querying users etc.)

## Setup ##
1. Clone this repo somewhere (home directory `~/` would do nicely)
1. Run `gnome-session-properties`
1. On the UI, click the _Add_ button
1. Enter a name (e.g. _ParanoidDaemon_)
1. For the _Command_, enter the path to (and including) _paranoid_daemon.py_
1. Click _Add_ and then _Close_
1. Log out and log back in again
1. ???
1. Profit

## The Command-Line Program ##

### Example Usage ###

#### Temporarily disabling notifications ####
Being spammed? Hate the notifications? Worry no more! (until your next login, anyway..)
```
.paranoid/paranoia.py silence
```
To re-enable, use
```
.paranoid/paranoia.py notify
```

#### Querying current users ####
To get all users currently connected:
```
.paranoid/paranoia.py get all
```
To get all users, except you, currently connected:
```
.paranoid/paranoia.py get others
```
To get your.. own.. details ..:
```
.paranoid/paranoia.py get me
```
