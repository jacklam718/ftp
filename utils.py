#!/usr/bin/env python
# --*--codig: utf8 --*--
import grp
import pwd
import time
import os
import stat

def fileProperty(filepath):
    """
    return information from given file, like this "-rw-r--r-- 1 User Group 312 Aug 1 2014 filename"
    """
    st = os.stat(filepath)
    fileMessage = [ ]
    def _getFileMode( ):
        modes = [
            stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR,
            stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP,
            stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH,
        ]
        mode     = st.st_mode
        fullmode = ''
        fullmode += os.path.isdir(filepath) and 'd' or '-'

        for i in range(9):
            fullmode += bool(mode & modes[i]) and 'rwxrwxrwx'[i] or '-'
        return fullmode

    def _getFilesNumber( ):
        return str(st.st_nlink)

    def _getUser( ):
        return pwd.getpwuid(st.st_uid).pw_name

    def _getGroup( ):
        return grp.getgrgid(st.st_gid).gr_name

    def _getSize( ):
        return str(st.st_size)

    def _getLastTime( ):
        return time.strftime('%b %d %H:%M', time.gmtime(st.st_mtime))
    for func in ('_getFileMode()', '_getFilesNumber()', '_getUser()', '_getGroup()', '_getSize()', '_getLastTime()'):
        fileMessage.append(eval(func))
    fileMessage.append(os.path.basename(filepath))
    return ' '.join(fileMessage)
