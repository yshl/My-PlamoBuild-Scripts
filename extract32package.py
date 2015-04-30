#!/usr/bin/python3
import tarfile
import sys
import os
import shutil

if len(sys.argv)<=1:
    sys.stderr.write("Usage: create32package.py x86-package\n")
    sys.exit(1)

def newpkgname(origfilename):
    ext=os.path.splitext(origfilename)[1]
    if ext in ['.gz', '.tgz']:
        mode='w:gz'
    elif ext in ['.bz2', '.tbz']:
        mode='w:bz2'
    elif ext in ['.xz', '.txz']:
        mode='w:xz'
    elif ext=='.tar':
        mode='w'
    else:
        sys.stderr.write(newfilename+' tgz, tbz or txz?\n')
        sys.exit(1)
    pkgname, others=os.path.basename(origfilename).split('-',1)
    return pkgname+'32-'+others, mode

def x64pkgname(origfilename):
    path, filename=os.path.split(origfilename)
    pkgname,version,arch,patch=filename.split('-')
    return "-".join([pkgname,version,'x86_64',patch])

def x32filter(member, x64filenames):
    if member.isdir():
        return True
    if member.name.startswith('install'):
        return True
    if member.name not in x64filenames:
        return True
    return False

x32filename=sys.argv[1]
newfilename,mode=newpkgname(x32filename)
x64filename=x64pkgname(x32filename)

with tarfile.open(x64filename, "r")as x64file:
    x64filenames=set(x64file.getnames())

infile=tarfile.open(x32filename, "r")
outfile=tarfile.open(newfilename, mode)

workdir='work'
os.mkdir(workdir)
try:
    os.chdir(workdir)
    try:
        for member in infile.getmembers():
            if x32filter(member, x64filenames):
                obj=infile.extractfile(member)
                if member.islnk():
                    member.type=tarfile.REGTYPE
                outfile.addfile(member, obj)
    finally:
        os.chdir('..')
finally:
    shutil.rmtree(workdir)

infile.close()
outfile.close()
