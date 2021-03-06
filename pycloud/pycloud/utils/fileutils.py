# KVM-based Discoverable Cloudlet (KD-Cloudlet) 
# Copyright (c) 2015 Carnegie Mellon University.
# All Rights Reserved.
# 
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER. CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY RIGHTS.
# 
# Released under a modified BSD license, please see license.txt for full terms.
# DM-0002138
# 
# KD-Cloudlet includes and/or makes use of the following Third-Party Software subject to their own licenses:
# MiniMongo
# Copyright (c) 2010-2014, Steve Lacy 
# All rights reserved. Released under BSD license.
# https://github.com/MiniMongo/minimongo/blob/master/LICENSE
# 
# Bootstrap
# Copyright (c) 2011-2015 Twitter, Inc.
# Released under the MIT License
# https://github.com/twbs/bootstrap/blob/master/LICENSE
# 
# jQuery JavaScript Library v1.11.0
# http://jquery.com/
# Includes Sizzle.js
# http://sizzlejs.com/
# Copyright 2005, 2014 jQuery Foundation, Inc. and other contributors
# Released under the MIT license
# http://jquery.org/license

#!/usr/bin/env python
#

import os
import os.path
import shutil
import stat
import fileinput
import sys
import re

from subprocess import Popen, PIPE

################################################################################################################
# Various file-related utility functions.
################################################################################################################

################################################################################################################
# Removes all contents of a folder. Exceptions can be added as a list (full path).
################################################################################################################
def remove_folder_contents(folder_path, exceptions=[]):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_path not in exceptions:
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

################################################################################################################
# Removes a folder and its contents (if they exist), and then creates the folder.
################################################################################################################
def recreate_folder(folder_path):
    # First remove it, if it exists.
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    # Now create it.
    create_folder_if_new(folder_path)

################################################################################################################
# Creates a folder path only if it does not exist.
################################################################################################################
def create_folder_if_new(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

################################################################################################################
# Protects a VM Image by making it read-only for all users.
################################################################################################################
def make_read_only_all(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.chmod(file_path,
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

################################################################################################################
# Makes the files of a VM Image available (read and write) to all users.
################################################################################################################
def make_read_write_all(file_path):
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.chmod(file_path,
                 stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)

################################################################################################################
# Changes ownership of the given file to the user running the script.
# NOTE: needs sudo permissions.
################################################################################################################
def chown_to_current_user(file_path):
    curr_user = os.geteuid()
    curr_group = os.getegid()

    # Execute sudo process to change ownership of potentially root owned file to the current user.
    p = Popen(['sudo', 'chown', str(curr_user) + ":" + str(curr_group), file_path], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    if rc != 0:
        print "Error getting ownership of file:\n%s" % err
        raise Exception("Error getting ownersip of file:\n%s" % err)

##############################################################################################################
# Replaces all occurrences of a given regular expression "original_text" with a new one "new_text" in the given file.
##############################################################################################################
def replace_in_file(original_text, new_text, file_path):
    # Iterate over all lines in the file, modifying it in place.
    regex = re.compile(original_text, re.IGNORECASE)
    if os.path.isfile(file_path):
        for line in fileinput.input(file_path, inplace=True):
            # Replace the string, if found in the current line.
            line = regex.sub(new_text, line)

            # Writes to stdout while using fileinput will replace the contents of the original file.
            sys.stdout.write(line)
    else:
        print 'File ' + file_path + ' not found, not replacing text.'


