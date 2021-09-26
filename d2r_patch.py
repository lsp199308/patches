import re

def get_build_id():
  with open("main", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

with open('main', 'rb') as fi:
    read_data = fi.read()
    result = re.search(b'\xb9...\x91...\x78...\xf9...\x94...\x36...\x94...\xf9...\xd2...\xf2...\xf2...\xcb...\xeb.......\x14', read_data)
    patch = "%06X%s%s" % (result.end(), "0004", "1F2003D5")
    text_file = open(get_build_id() + ".ips", "wb")
    print("d2r build-id: " + get_build_id())
    print("d2r offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()