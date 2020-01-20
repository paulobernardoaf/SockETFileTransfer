# SockETFileTransfer

SockETFileTransfer is an application for transferring files between clients using sockets.

Server runs in the background and utilizes threads to handle multiple clients.

Clients can:
- Add files to the queue and send them to multiple clients.
- View which files were received.
- Delete received files from disk.

# Dependencies

## Python
Version 3.5 to 3.7 (3.8 is incompatible with Kivy 1.11.0)

## Python packages
Remember to use pip3 on all commands.

- Kivy - 1.11.0 ( [Download Kivy](https://kivy.org/#download) )
  + Kivy is a python library for implementing GUI applications.
- hurry - 0.9 ( pip3 install hurry.filesize )

# Running
\<python  command\> can  be  ”py”,  ”python”,  ”python3”,  make  sure  that  the command that you run will use Python3.

## Server
To run the server go to the server directory and run the following command:
```
  <python command> server.py
```

## Client
To run the client go to the client directory and run the following command:
```
  <python command> app.py
```

Even if you run multiple clients from the same directory, as long that the clients usernames are different, each client will create a new directory for the received files to avoid conflicts. The directory for the received files is named with the username to when the same user log in again, their received files will be there.
