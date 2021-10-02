Todo list:

* format the guides more nicely
* potentially whitelist commits from people who aren't incompetent or malicious
* publish patches to this repository and configure auto-publishing on new commits (configured suppository by adding in patches as submodule https://github.com/borntohonk/suppository/blob/master/update_patches.sh)
* adjust es/fs guides to be more understandable (better formatting and corrections)

* [Part 1A detailing how to set up ghidra and the switch loader for windows](Part1A-WindowsSetup.MD)
* [Part 1B detailing how to set up ghidra and the switch loader for linux](Part1B-LinuxSetup.MD)
* [Part 2 detailing how to to use ghidra to from ground up make a patch for nifm.](Part2.MD)
* [Python script to generate nifm patches, usage: place uncompressed nifm as "main" in the same folder then use "python3 nifm_patch.py" (pattern applicable for 12.0.0 and up)](nifm_patch.py)
* [Guide describing how to patch out the online check in Diablo 2 Resurrected - TitleID 0100726014352000/0100726014352800.](D2R-0100726014352800-65536-v131072.md)
* [Python script to generate D2R patches, usage: place uncompressed D2R as "main" in the same folder then use "python3 d2r_patch.py"](d2r_patch.py)
* [Guide describing how to patch FS, - TitleID 0100000000000819/010000000000081B.](FS-010000000000081B-0100000000000819.md)
* [Python script to generate FS patches, usage: place uncompressed_exfat.kip1, compressed_exfat.kip1 and compressed_fat32.kip1 in the same folder then use "python3 fs_patch.py"](fs_patch.py)
* [Guide describing how to patch ES, - TitleID 0100000000000033.](ES-0100000000000033.md)
* [Python script to generate ES patches, usage: place uncompressed ES as "main" in the same folder then use "python3 es_patch.py"](es_patch.py)



* [Python script to process dumped FW files from system partition and make patches for the system firmware version that was dumped. Usage: make a directory in the organize folder (example 1300 for 13.0.0, or just generic "firmware" instead of numbered folders, anything works.), then place the dumped nca.00/nca files/folders (both works) in a sub-folder called "nca" (example: organize/1300/nca/*.nca), then use "python3 organize.py". The patches will be output to the atmosphere folder, ready to be packed up and pushed as a release](organize/organize.py)

Other guides will be linked in this README.md but be be published without any context of the previous guides, assuming the tutorial on how to do things is over. part 1 and part 2 are considered the tutorial.

-Credits: me (@borntohonk)
