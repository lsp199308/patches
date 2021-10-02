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
  with open(version + "/ues.nso0", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

def get_nifm_build_id():
  with open(version + "/unifm.nso0", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

class CNMT:
    title_types = {
        0x1: 'SystemProgram',
        0x2: 'SystemData',
        0x3: 'SystemUpdate',
        0x4: 'BootImagePackage',
        0x5: 'BootImagePackageSafe',
        0x80:'Application',
        0x81:'Patch',
        0x82:'AddOnContent',
        0x83:'Delta'
    }
    nca_types  = {
        0:'Meta',
        1:'Program',
        2:'Data',
        3:'Control',
        4:'HtmlDocument',
        5:'LegalInformation',
        6:'DeltaFragment'
    }
    def __init__(self, fp):
        self.f = fp
        self._parse()

    def _parse(self):
        self.title_type = self.title_types[read_u8(self.f, 0xC)]
        self.tid        = read_u64(self.f, 0x0)
        self.ver        = read_u32(self.f, 0x8)
        self.sysver     = read_u64(self.f, 0x28)
        self.dlsysver   = read_u64(self.f, 0x18)

        self.data = {}
        if self.title_type == 'SystemUpdate':
            self.titles_nb = 0
            entries_nb = read_u16(self.f, 0x12)
            for n in range(entries_nb):
                self.titles_nb += 1
                offset = 0x20 + 0x10 * n
                tid        = read_u64(self.f, offset)
                ver        = read_u32(self.f, offset + 0x8)
                title_type = self.title_types[read_u8(self.f, offset + 0xC)]
                self.data[tid] = {
                    'Version': ver,
                    'Type':    title_type
                }
        else:
            self.files_nb   = 0
            self.title_size = 0
            for nca_type in list(self.nca_types.values()):
                self.data[nca_type] = {}
            table_offset = read_u16(self.f,0xE)
            entries_nb = read_u16(self.f, 0x10)
            for n in range(entries_nb):
                offset = 0x20 + table_offset + 0x38 * n
                hash = read_at(self.f, offset, 0x20)
                ncaid = int.from_bytes(read_at(self.f, offset + 0x20, 0x10), byteorder='big')
                size = read_u48(self.f, offset + 0x30)
                nca_type = self.nca_types[read_u16(self.f, offset+0x36)]
                self.data[nca_type][ncaid] = {
                    'Size': size,
                    'Hash': hash
                }
                self.files_nb   += 1
                self.title_size += size

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

versions = {
    450:       "0.0.0.450",
    65796:     "0.0.1.260",
    131162:    "0.0.2.90",
    196628:    "0.0.3.20",
    262164:    "0.0.4.20",
    201327002: "3.0.0.410",
    201392178: "3.0.1.50",
    201457684: "3.0.2.20",
    268435656: "4.0.0.200",
    268501002: "4.0.1.10",
    269484082: "4.1.0.50",
    335544750: "5.0.0.430",
    335609886: "5.0.1.30",
    335675432: "5.0.2.40",
    336592976: "5.1.0.80",
    402653544: "6.0.0.360",
    402718730: "6.0.1.10",
    403701850: "6.1.0.90",
    404750376: "6.2.0.40",
    469762248: "7.0.0.200",
    469827614: "7.0.1.30",
    536871442: "8.0.0.530",
    536936528: "8.0.1.80",
    537919608: "8.1.0.120",
    537985054: "8.1.1.30",
    603980216: "9.0.0.440",
    604045412: "9.0.1.100",
    605028592: "9.1.0.240",
    606076948: "9.2.0.20",
    671089000: "10.0.0.360",
    671154196: "10.0.1.20",
    671219752: "10.0.2.40",
    671285268: "10.0.3.20",
    671350804: "10.0.4.20",
    672137336: "10.1.0.120",
    672202772: "10.1.1.20",
    673185852: "10.2.0.60",
    738197944: "11.0.0.440",
    738263060: "11.0.1.20",
    738264040: "11.0.1.1000",
    805308888: "12.0.0.2520",
    805371944: "12.0.1.40",
    805437460: "12.0.2.20",
    805502996: "12.0.3.20",
    806355064: "12.1.0.120"
}

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

    if version == "updaters":
        continue

    # Rename CNMTs to make them easier to find. Also, if nca is a folder,
    # get its content. Also, get the hash, and give it the proper ncaid name
    print(f"===== Handling {version} =====")

    HACTOOL_PROGRAM = "hactool"
    if os.path.isfile(version + "/dev"):
        HACTOOL_PROGRAM += " --dev"

    print(f"# Normalizing the nca folder")
    for nca in os.listdir(version + "/nca"):
        ncaFull = version + "/nca/" + nca
        # Fix "folder-as-file" files when dumped from Switch NAND
        if os.path.isdir(ncaFull):
            print_verbose(f"{ncaFull}/00 -> {ncaFull}")
            os.rename(ncaFull, ncaFull + "_folder")
            os.rename(ncaFull + "_folder/00", ncaFull)
            os.rmdir(ncaFull + "_folder")
        # Ensure the NCAID is correct (It's wrong when dumped from the
        # Placeholder folder on a Switch NAND
        ncaid = get_ncaid(ncaFull)
        newName = version + "/nca/" + ncaid + "." + ".".join(os.path.basename(ncaFull).split(".")[1:])
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
    for nca in os.listdir(version + "/nca"):
        ncaFull = version + "/nca/" + nca
        process = subprocess.Popen(["sh", "-c", HACTOOL_PROGRAM + " '" + ncaFull + "' | grep 'Title ID:' | awk '{print $3}'"], stdout=subprocess.PIPE)
        titleId = process.communicate()[0].split(b"\n")[0].decode('utf-8')
        process = subprocess.Popen(["sh", "-c", HACTOOL_PROGRAM + " '" + ncaFull + "' | grep 'Content Type:' | awk '{print $3}'"], stdout=subprocess.PIPE)
        contentType = process.communicate()[0].split(b"\n")[0].decode('utf-8')

        mkdirp(version + "/titleid/" + titleId)

        print_verbose(version + "/titleid/" + titleId + "/" + contentType + ".nca -> " + "../../nca/" + nca)
        symlink_force("../../nca/" + nca, version + "/titleid/" + titleId + "/" + contentType + ".nca")

    print("# Extracting ES")
    esFull = version + "/"
    ncaParent = version + "/titleid/0100000000000033"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/0100000000000033/exefs/main"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnca '{version}/titleid/0100000000000033/Program.nca' --exefsdir '{version}/titleid/0100000000000033/exefs/'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnso0 '{ncaFull}' --uncompressed '{version}/ues.nso0'"], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting NIFM")
    nifmFull = version + "/"
    ncaParent = version + "/titleid/010000000000000f"
    ncaPartial = ncaParent + "/Program.nca"
    ncaFull = version + "/titleid/010000000000000f/exefs/main"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnca '{version}/titleid/010000000000000f/Program.nca' --exefsdir '{version}/titleid/010000000000000f/exefs/'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tnso0 '{ncaFull}' --uncompressed '{version}/unifm.nso0'"], stdout=subprocess.DEVNULL)
    process.wait()

    print("# Extracting fat32")
    ncaParent = version + "/titleid/0100000000000819"
    pk21dir = ncaParent + "/package2"
    ini1dir = ncaParent + "/ini1"
    ncaFull = ncaParent + "/Data.nca"
    fat32Full = version + "/u_fat32FS.kip1"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaFull}' -tnca --romfsdir '{ncaParent}/romfs'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tpk21 '{ncaParent}/romfs/nx/package2' --ini1dir '{ini1dir}'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaParent}/ini1/FS.kip1' -tkip1 --uncompressed='{fat32Full}'"], stdout=subprocess.DEVNULL)
    process.wait()
    fat32Compressed = version + "/titleid/0100000000000819/ini1/FS.kip1"
    fsCopy = version  + "/fat32FS.kip1"
    process = shutil.copyfile(fat32Compressed, fsCopy)
    
    print("# Extracting exfat")
    ncaParent = version + "/titleid/010000000000081b"
    pk21dir = ncaParent + "/package2"
    ini1dir = ncaParent + "/ini1"
    ncaFull = ncaParent + "/Data.nca"
    exfatFull = version + "/u_exfatFS.kip1"
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaFull}' -tnca --romfsdir '{ncaParent}/romfs'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} -tpk21 '{ncaParent}/romfs/nx/package2' --package2dir '{pk21dir}' --ini1dir '{ini1dir}'"], stdout=subprocess.DEVNULL)
    process.wait()
    process = subprocess.Popen(["sh", "-c", f"{HACTOOL_PROGRAM} '{ncaParent}/ini1/FS.kip1' -tkip1 --uncompressed='{exfatFull}'"], stdout=subprocess.DEVNULL)
    process.wait()
    exfatCompressed = version + "/titleid/010000000000081b/ini1/FS.kip1"
    fsCopy = version  + "/exfatFS.kip1"
    process = shutil.copyfile(exfatCompressed, fsCopy)

    print("# Making sigpatches")
    esuncompressed = version + "/ues.nso0"
    nifmuncompressed = version + "/unifm.nso0"
    exfatuncompressed = version + "/u_exfatFS.kip1"
    fat32uncompressed = version + "/u_fat32FS.kip1"
    fat32compressed = version + "/exfatFS.kip1"
    exfatcompressed = version + "/fat32FS.kip1"

    with open(esuncompressed, 'rb') as fi:
        read_data = fi.read()
    result = re.search(b'\x1f\x01\x09\xeb\x61\x00\x00\x54\xf3\x03\x1f\xaa\x02\x00\x00\x14\x33\xd2\x85\x52\xe0.\x00\x91.{3}\x94.\x63\x00.{3}\x00\x94\xa0.{2}\xd1.{2}\xff\x97', read_data)
    patch = "%06X%s%s" % (result.end(), "0004", "E0031FAA")
    text_file = open("../atmosphere/exefs_patches/es_patches/" + get_es_build_id() + ".ips", "wb")
    print("es build-id: " + get_es_build_id())
    print("es offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()
    fi.close()

    with open(nifmuncompressed, 'rb') as fi:
        read_data = fi.read()
    result = re.search(b'.{16}\xf5\x03\x01\xaa\xf4\x03\x00\xaa.{4}\xf3\x03\x14\xaa\xe0\x03\x14\xaa\x9f\x02\x01\x39\x7f\x8e\x04\xf8.{4}\xe0\x03\x14\xaa\xe1\x03\x15\xaa.{4}', read_data)
    text_file = open("../atmosphere/exefs_patches/nifm_ctest/" + get_nifm_build_id() + ".ips", "wb")
    patch = "%06X%s%s" % (result.start(), "0008", "E0031FAAC0035FD6")
    print("nifm build-id: " + get_nifm_build_id())
    print("nifm offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()
    fi.close()

    with open(exfatuncompressed, 'rb') as fi1:
        read_data = fi1.read()
        result1 = re.search(b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)
        result2 = re.search(b'.{3}\xaa.{3}\x97.{3}\x36.{3}\x91.{3}\xaa.{7}\xaa.{11}\xaa.{7}\x52.{3}\x72.{3}\x97', read_data)
        patch1 = "%06X%s%s" % (result1.end(), "0004", "E0031F2A")
        patch2 = "%06X%s%s" % (result2.end(), "0004", "1F2003D5")
        exfathash = hashlib.sha256(open(exfatcompressed, 'rb').read()).hexdigest().upper()
        print("found FS first offset and patch at: " + patch1)
        print("found FS second offset and patch at: " + patch2)
        print("exfat sha256: " + exfathash)
        text_file = open('../atmosphere/kip_patches/fs_patches/%s.ips' % exfathash, 'wb')
        text_file.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
        text_file.close()
        fat32hash = hashlib.sha256(open(fat32compressed, 'rb').read()).hexdigest().upper()
        print("fat32 sha256: " + fat32hash)
        text_file = open('../atmosphere/kip_patches/fs_patches/%s.ips' % fat32hash, 'wb')
        text_file.write(bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46")))
        text_file.close()
        text_file = open('../hekate_patches/' + version + '-fat32.ini', 'w')
        text_file.write("#FS " + version + "-fat32\n")
        text_file.write("[FS:" + '%s' % fat32hash[:16] + "]\n")
        hekate_bytes = fi1.seek(result1.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',E0031F2A\n')
        hekate_bytes = fi1.seek(result2.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result2.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',1F2003D5\n')
        text_file.close()
        text_file = open('../hekate_patches/' + version + '-exfat.ini', 'w')
        text_file.write("#FS " + version + "-exfat\n")
        text_file.write("[FS:" + '%s' % exfathash[:16] + "]\n")
        hekate_bytes = fi1.seek(result1.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result1.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',E0031F2A\n')
        hekate_bytes = fi1.seek(result2.end())
        text_file.write('.nosigchk=0:0x' + '%05X' % (result2.end()-0x100) + ':0x4:' + fi1.read(0x4).hex().upper() + ',1F2003D5\n')
    fi1.close()

    print("# Verifying the dump is complete")
    process = subprocess.run(["sh", "-c", f"{HACTOOL_PROGRAM} '{version}/titleid/0100000000000816/Meta.nca' -tnca --section0dir '{version}/titleid/0100000000000816/section0'"], stdout=subprocess.DEVNULL)