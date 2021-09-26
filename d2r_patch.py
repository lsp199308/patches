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
    result = re.findall(b'\xb9...\x91...\x78...\xf9...\x94...\x36...\x94...\xf9...\xd2...\xf2...\xf2...\xcb...\xeb.......\x14', read_data)[0]
    i = read_data.find(result)

    while i >= 0:
        i += len(result)
        d2r_offset = ("%02X"%i)
        i = read_data.find(result, i)
    build_id()
    text_file = open(buildid + ".ips", "wb")
    print("d2r build-id: " + buildid)
    print ("found at offset: " + d2r_offset)
    y = bytes.fromhex(str("5041544348" + d2r_offset + "00041F2003D5454F46"))

    text_file.write(y)
    text_file.close()

    