#!/usr/bin/env python

VERBOSE = False

import os
import subprocess
import shutil
import errno
import hashlib
import re
from pathlib import Path

def get_es_build_id():
  with open("uncompressed_es.nso0", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

def get_nifm_build_id():
  with open("uncompressed_nifm.nso0", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

def mkdirp(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def symlink_force(target, link_name):
    try:
        os.symlink(target, link_name)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(link_name)
            os.symlink(target, link_name)
        else:
            raise e

def get_ncaid(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()[:32]

def print_verbose(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

for version in os.listdir("."):
    # Ignore files (only treat directories)
    if os.path.isfile(version):
        continue

    # Rename CNMTs to make them easier to find. Also, if nca is a folder,
    # get its content. Also, get the hash, and give it the proper ncaid name
    print(f"===== Handling firmware files =====")

    HACTOOL_PROGRAM = "hactool"
    if os.path.isfile(version + "/dev"):
        HACTOOL_PROGRAM += " --dev"

    print(f"# Normalizing the nca folder")
    for nca in os.listdir(version):

        ncaFull = version + "/" + nca
        # Fix "folder-as-file" files when dumped from Switch NAND
        if nca == "titleid":
            continue
        if os.path.isdir(ncaFull):
            print_verbose(f"{ncaFull}/00 -> {ncaFull}")
            os.rename(ncaFull, ncaFull + "_folder")
            os.rename(ncaFull + "_folder/00", ncaFull)
            os.rmdir(ncaFull + "_folder")
        # Ensure the NCAID is correct (It's wrong when dumped from the
        # Placeholder folder on a Switch NAND
        ncaid = get_ncaid(ncaFull)
        newName = version + "/" + ncaid + "." + ".".join(os.path.basename(ncaFull).split(".")[1:])
        print_verbose(f"{ncaFull} -> {newName}")
        os.rename(ncaFull, newName)
        ncaFull = newName

        # Ensure meta files have .cnmt.nca extension
        process = subprocess.Popen(["sh", "-c", HACTOOL_PROGRAM + " '" + ncaFull + "' | grep 'Content Type:' | awk '{print $3}'"], stdout=subprocess.PIPE)
        contentType = process.communicate()[0].split(b"\n")[0].decode('utf-8')
        if contentType == "Meta" and not nca.endswith(".cnmt.nca"):
            print_verbose(ncaFull + " -> " + ".".join(ncaFull.split(".")[:-1]) + ".cnmt.nca")
            shutil.move(ncaFull, ".".join(ncaFull.split(".")[:-1]) + ".cnmt.nca")

    print("# Sort by titleid")
    for nca in os.listdir(version):
        ncaFull = version + "/" + nca
        process = subprocess.Popen(["sh", "-c", HACTOOL_PROGRAM + " '" + ncaFull + "' | grep 'Title ID:' | awk '{print $3}'"], stdout=subprocess.PIPE)
        titleId = process.communicate()[0].split(b"\n")[0].decode('utf-8')
        process = subprocess.Popen(["sh", "-c", HACTOOL_PROGRAM + " '" + ncaFull + "' | grep 'Content Type:' | awk '{print $3}'"], stdout=subprocess.PIPE)
        contentType = process.communicate()[0].split(b"\n")[0].decode('utf-8')

        mkdirp(version + "/titleid/" + titleId)

        print_verbose(version + "/titleid/" + titleId + "/" + contentType + ".nca -> " + "../../" + nca)
        symlink_force("../../" + nca, version + "/titleid/" + titleId + "/" + contentType + ".nca")

    print("# Extracting ES")
    esFull = version + "/"
    ncaParent = version + "/titleid/0100000000000033"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/0100000000000033/exefs/main"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnca '{version}/titleid/0100000000000033/Program.nca' --exefsdir '{version}/titleid/0100000000000033/exefs/'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnso0 '{ncaFull}' --uncompressed 'uncompressed_es.nso0'"], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting NIFM")
    nifmFull = version + "/"
    ncaParent = version + "/titleid/010000000000000f"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/010000000000000f/exefs/main"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnca '{version}/titleid/010000000000000f/Program.nca' --exefsdir '{version}/titleid/010000000000000f/exefs/'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnso0 '{ncaFull}' --uncompressed 'uncompressed_nifm.nso0'"], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting fat32")
    ncaParent = version + "/titleid/0100000000000819"
    pk21dir = ncaParent + "/package2"
    ini1dir = ncaParent + "/ini1"
    ncaFull = ncaParent + "/Data.nca"
    fat32Full = "uncompressed_fat32.kip1"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaFull}' -tnca --romfsdir '{ncaParent}/romfs'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tpk21 '{ncaParent}/romfs/nx/package2' --ini1dir '{ini1dir}'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaParent}/ini1/FS.kip1' -tkip1 --uncompressed='{fat32Full}'"], stdout=subprocess.DEVNULL)
    process.wait()
    fat32Compressed = version + "/titleid/0100000000000819/ini1/FS.kip1"
    fsCopy = "compressed_fat32.kip1"
    process = shutil.copyfile(fat32Compressed, fsCopy)
    
    print("# Extracting exfat")
    ncaParent = version + "/titleid/010000000000081b"
    pk21dir = ncaParent + "/package2"
    ini1dir = ncaParent + "/ini1"
    ncaFull = ncaParent + "/Data.nca"
    exfatFull = "uncompressed_exfat.kip1"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaFull}' -tnca --romfsdir '{ncaParent}/romfs'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tpk21 '{ncaParent}/romfs/nx/package2' --package2dir '{pk21dir}' --ini1dir '{ini1dir}'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaParent}/ini1/FS.kip1' -tkip1 --uncompressed='{exfatFull}'"], stdout=subprocess.DEVNULL)
    process.wait()
    exfatCompressed = version + "/titleid/010000000000081b/ini1/FS.kip1"
    fsCopy = "compressed_exfat.kip1"
    process = shutil.copyfile(exfatCompressed, fsCopy)

for version in os.listdir("."):
    # Ignore files (only treat directories)
    if os.path.isfile(version):
        continue

    print(f"===== Printing relevant hashes and buildids =====")

    HACTOOL_PROGRAM = "hactool"
    if os.path.isfile(version + "/dev"):
        HACTOOL_PROGRAM += " --dev"

    esuncompressed = "uncompressed_es.nso0"
    nifmuncompressed = "uncompressed_nifm.nso0"
    fat32compressed = "compressed_exfat.kip1"
    exfatcompressed = "compressed_fat32.kip1"

    print("es build-id: " + get_es_build_id())
    print("nifm build-id: " + get_nifm_build_id())
    exfathash = hashlib.sha256(open(exfatcompressed, 'rb').read()).hexdigest().upper()
    print("exfat sha256: " + exfathash)
    fat32hash = hashlib.sha256(open(fat32compressed, 'rb').read()).hexdigest().upper()
    print("fat32 sha256: " + fat32hash)