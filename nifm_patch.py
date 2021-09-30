import re, struct

def build_id():
    global text_offset
    global text_size
    global buildid
    with open("main", "rb") as f:
        f.seek(0x10)
        text_offset = struct.unpack('<I',f.read(4))[0]
        f.seek(0x18)
        text_size = struct.unpack('<I',f.read(4))[0]
        f.seek(0x40)
        raw_buildid = f.read(0x14)
        buildid = raw_buildid.hex().upper()
        f.close
    text_offset *= 8
    text_size *= 8

with open('main', 'rb') as fi:
    read_data = fi.read()
    result = re.search(b'.{16}\xf5\x03\x01\xaa\xf4\x03\x00\xaa.{4}\xf3\x03\x14\xaa\xe0\x03\x14\xaa\x9f\x02\x01\x39\x7f\x8e\x04\xf8.{4}\xe0\x03\x14\xaa\xe1\x03\x15\xaa.{4}', read_data)
    nifm_offset = (hex (result.start()))[2:]
    build_id()
    text_file = open(buildid + ".ips", "wb")
    print("nifm build-id: " + buildid)
    print ("found at offset: " + nifm_offset)
    y = bytes.fromhex(str("50415443480" + nifm_offset + "0008E0031FAAC0035FD6454F46"))

    text_file.write(y)
    text_file.close()