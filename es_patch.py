import re

def get_build_id():
  with open("main", "rb") as f:
    f.seek(0x40)
    return(f.read(0x14).hex().upper())

with open('main', 'rb') as fi:
    read_data = fi.read()
    result = re.search(b'\x1f\x01\x09\xeb\x61\x00\x00\x54\xf3\x03\x1f\xaa\x02\x00\x00\x14\x33\xd2\x85\x52\xe0.\x00\x91.{3}\x94.\x63\x00.{3}\x00\x94\xa0.{2}\xd1.{2}\xff\x97', read_data)
    patch = "%06X%s%s" % (result.end(), "0004", "E0031FAA")
    text_file = open(get_build_id() + ".ips", "wb")
    print("es build-id: " + get_build_id())
    print("es offset and patch at: " + patch)
    text_file.write(bytes.fromhex(str("5041544348" + patch + "454F46")))
    text_file.close()