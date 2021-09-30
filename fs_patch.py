import re, hashlib
with open('uncompressed_exfat.kip1', 'rb') as fi1:
    read_data = fi1.read()
    result1 = re.findall(b'.{3}\x12.{3}\x71.{3}\x54.{3}\x12.{3}\x71.{3}\x54.{3}\x36.{3}\xf9', read_data)[0]

    i1 = read_data.find(result1)
    while i1 >= 0:
        i1 += len(result1)
        fs_offset_1 = ("%02X "%i1)
        i1 = read_data.find(result1, i1)

    result2 = re.findall(b'.{3}\xaa.{3}\x97.{3}\x36.{3}\x91.{3}\xaa.{7}\xaa.{11}\xaa.{7}\x52.{3}\x72.{3}\x97', read_data)[0]
    i2 = read_data.find(result2)
    while i2 >= 0:
        i2 += len(result2)
        fs_offset_2 = ("%02X "%i2)
        i2 = read_data.find(result2, i2)

    patch1 = "0" + fs_offset_1 + "0004" + "E0031F2A"
    patch2 = "0" + fs_offset_2 + "0004" + "1F2003D5"
    exfathash = hashlib.sha256(open('compressed_exfat.kip1', 'rb').read()).hexdigest().upper()
    print ("found first offset at: " + fs_offset_1)
    print ("found second offset at: " + fs_offset_2)
    print("exfat sha256: " + exfathash)
    text_file = open('%s.ips' % exfathash, 'wb')
    y = bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46"))
    text_file.write(y)
    text_file.close()
    fat32hash = hashlib.sha256(open('compressed_fat32.kip1', 'rb').read()).hexdigest().upper()
    print("fat32 sha256: " + fat32hash)
    y = bytes.fromhex(str("5041544348" + patch1 + patch2 + "454F46"))
    text_file = open('%s.ips' % fat32hash, 'wb')
    text_file.write(y)
    text_file.close()