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
    result = re.findall(b'\x1f\x01\x09\xeb\x61\x00\x00\x54\xf3\x03\x1f\xaa\x02\x00\x00\x14\x33\xd2\x85\x52\xe0.\x00\x91.{3}\x94.\x63\x00.{3}\x00\x94\xa0.{2}\xd1.{2}\xff\x97', read_data)[0]
    i = read_data.find(result)

    while i >= 0:
        i += len(result)
        es_offset = ("%02X"%i)
        i = read_data.find(result, i)
    build_id()
    text_file = open(buildid + ".ips", "wb")
    print("es build-id: " + buildid)
    print ("found at offset: " + es_offset)
    y = bytes.fromhex(str("50415443480" + es_offset + "0004E0031FAA454F46"))

    text_file.write(y)
    text_file.close()

    