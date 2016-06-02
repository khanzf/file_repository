from file_repository.models import Inode
import os, re

# Recursive function to delete both files and directories
def del_inode(inode):
    # Recursively go through all subdirectories
    directories = inode.inodes.filter(is_directory = True)
    for dir_inode in directories:
        del_inode(dir_inode) 
    # Now delete them all
    directories.all().delete()
    # And then wipe out the files
    files = inode.inodes.filter(is_directory = False)
    for subfile in files:
        os.remove(subfile.name) # Delete files from the HD
    # Now delete the inode links from the DB
    files.all().delete()

def create_root(rootname):
    new_root = Inode(name='', rootname=rootname, is_directory=True)
    new_root.save()
    return new_root

def create_file(parent, name, content):
    new_file = Inode(is_directory=False)
    new_file.content = content
    new_file.name = name
    new_file.save()
    parent.inodes.add(new_file)
    return new_file

def create_directory(parent, name):
    new_directory = Inode(is_directory=True)
    new_directory.name = name
    new_directory.save()
    parent.inodes.add(new_directory)
    return new_directory

def get_inode(filedir, rootname):

    try:
        rootdirectory = Inode.objects.get(rootname=rootname,
                                          name='/',
                                          is_directory=True)
    except Inode.DoesNotExist:
        error_inode = Inode(rootname=rootname, name='/', is_directory=True)
        error_inode.error = 500 
        return error_inode

    if filedir == None:
        return rootdirectory

    current_directory = rootdirectory
    tempurl = filedir
    while tempurl:
        lastnode = re.match('^([\w|\-|\.]+)(\/?)$', tempurl) 
        if lastnode is not None:
            try:
                if lastnode.group(2) is '' or lastnode.group(2) is '/':
                    lastinode = current_directory.inodes.get(name=lastnode.group(1))
                    return lastinode
            except Inode.DoesNotExist:
                current_directory.error = 404
                return current_directory

        print("----------> %s" % tempurl)
#        response = re.match('^([\w|\-|\.\ ]+)\/(.+)', tempurl)
        response = re.match('^([\w\-\.\ ]+)\/([\w\-\.\ \/]+)', tempurl)
        if response == None:
            continue
        tree, tempurl = response.groups()
        if tree: # This is a directory
            current_directory = current_directory.inodes.get(name=tree, is_directory=True)
            continue

def get_inode_old(filedir, rootname):

    # Get rid of the first /
    if len(filedir) is not 0 and filedir[0] == '/':
        return (301, None, None, '')

    # Get rid of //'s, do a redirection if necessary
    if filedir != None:
        tempurl = filedir
        while True:
            newtempurl = tempurl.replace('//', '/')
            if newtempurl == tempurl:
                break
            tempurl = newtempurl
        if filedir != tempurl:
            return (301, None, None, ('' if tempurl[:1]=='/' else '/') + tempurl)
        ### End of the block
        filedir = tempurl
    else:
        tempurl = filedir
    # End of redirection block

    # Set their default values, starting at the root directory
    current_directory = Inode.objects.get(rootname=rootname)
    current_file = None

    ### Find the path
    while tempurl:
        # Check if its the last node
        lastnode = re.match('^([\w|\-|\.]+)\/?$', tempurl)
        if lastnode: #
            if current_directory.inodes.filter( name=lastnode.group(1), is_directory=True ).count() == 1:
                # We've found that its a directory, keep going
                current_directory = current_directory.inodes.get(name=lastnode.group(1), is_directory=True)
            elif current_directory.inodes.filter( name=lastnode.group(1), is_directory=False ).count() == 1:
                # Its a file, send back the file
                current_file = current_directory.inodes.get(name=lastnode.group(1), is_directory=False) 
                return (200, current_directory, current_file, None)
            else:
                return (404, None, None, None)
            break

        tree = re.match('^([\w|\-|\.]+)\/(.+)', tempurl)
        # Not the last node, then its a Directory
        if tree: # This is a directory
            new_subdir = tree.group(1)
            tempurl = tree.group(2)
            try:
                current_directory = current_directory.inodes.get(name=new_subdir, is_directory=True)
            except Inode.DoesNotExist:
                return (404, None, None, None)
        else:
            break
    ### End of finding the path

    ### If its a directory, put in trailing /
    if current_file == None: # Its a directory
        if filedir == '':
            pass
        elif filedir != None and filedir[-1:] != '/':
            return (301, None, None, filedir + '/')
    ### Accept final trialing /

    # Send back the local directory
    return (200, current_directory, None, None)
