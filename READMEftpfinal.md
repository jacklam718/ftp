About this project
==================
This is FTP server & client, client using PyQt GUI framework

FTP is a protocol for transferring files between systems over a TCP network. It was first developed in 1971 and has since been widely adopted as an effective way to share large files over the internet.
File Transfer Protocol (often abbreviated FTP) is an application- layer protocol.

We can list the root directory using this little snippet:

```bash
$ import ftplib

$ ftp = ftplib.FTP("ftp.nluug.nl")
$ ftp.login("anonymous", "ftplib-example-1")

$ data = []

$ ftp.dir(data.append)

$ ftp.quit()

$ for line in data:
    $ print "-", line
```

This will output the directory contents. in a simple console style output. 
If you want to show a specific directory you must change the directory after connecting with the ftp.cwd(‘/‘) function where the parameter is the directory you want to change to.
```bash
$ import ftplib

$ ftp = ftplib.FTP("ftp.nluug.nl")
$ ftp.login("anonymous", "ftplib-example-1")

$ data = []

$ ftp.cwd('/pub/')         # change directory to /pub/
$ ftp.dir(data.append)

$ ftp.quit()

$ for line in data:
    $ print "-", line
```
## Download file
To download a file we use the retrbinary() function. An example below:
```bash
$ import ftplib
$ import sys

$ def getFile(ftp, filename):
   $ try:
       $ ftp.retrbinary("RETR " + filename ,open(filename, 'wb').write)
   $ except:
       $ print "Error"
```
```bash
$ ftp = ftplib.FTP("ftp.nluug.nl")
$ ftp.login("anonymous", "ftplib-example-1")

$ ftp.cwd('/pub/')         # change directory to /pub/
$ getFile(ftp,'README.md')

$ ftp.quit()
```
## Uploading files
We can upload files using the storlines() command. This will upload the file README.nluug in the main directory. If you want to upload in another directory combine it with the cwd() function.
```bash
$ import ftplib
$ import os

$ def upload(ftp, file):
    $ ext = os.path.splitext(file)[1]
    $ if ext in (".txt", ".htm", ".html"):
        $ ftp.storlines("STOR " + file, open(file))
   $ else:
       $ ftp.storbinary("STOR " + file, open(file, "rb"), 1024)

$ ftp = ftplib.FTP("127.0.0.1")
$ ftp.login("username", "password")

$ upload(ftp, "README.md")
```

## Why I create this project?
Because Qt framework seems a powerful and interesting framework, so I want to learn and try this framework. Another reason I'm interested about `Internet Protocol` including the FTP Protocol so I want to try to implement FTP Protocol.

## Dependencies
PyQt4.x

## Tested on
`Python2.7` & `python3.5`

## Usage
```bash
$ python ftp_server.py
$ python ftp_client.py
```

>Note:
When you run ftp_server.py you may need permission because the ftp server port default run on 20 & 21, may you can run `sudo python ftp_server.py`

## Platform
Currently can only run on Linux like OS e.g Ubuntu, Mac OSX etc.

