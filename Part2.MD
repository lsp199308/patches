Part 2 of this guide assumes you have succesfully set up ghidra as described in Part1A (for windows users) or Part1B (for linux users).

Part2 will go through the basics of getting the type of switch binaries you need. To proceed you will need hactool (https://github.com/SciresM/hactool) for opening switch binaries, the binaries for hactool can be gotten from the artifacts (requires logging into github) or compiling it yourself. Lockpick_RCM (https://github.com/shchmue/Lockpick_RCM) for getting the keys required for hactool to open said switch binaries. Set up an enviroment variable for hactool / place it /usr/local/bin/hactool if you're a linux user.

Part 2 also assumes you have python 3 installed.

1. Run the lockpick_RCM binary on a nintendo switch capable of doing so.
2. Copy the outputting prod.keys (located on your switch sd card at /switch/prod.keys) to ~/.switch/prod.keys (this translates to /home/youruser/.switch/prod.keys and C:/users/youruser/.switch/prod.keys).
3. Run "hactool -t keygen" in your terminal/cmd prompt to verify it populates a list of keys.
4. Assuming you completed step 3 and it does produce a list of keys, you should now be capable of extracting .ncas, this specific guide (part 2) will cover system firmware files.
5. Dump your own system version files or get them from https://darthsternie.net/switch-firmwares/ this specific example will will use the latest version at the time of writing this, 13.0.0
6. Organize the .nca containers in a fashion that lets you identify them more easily with tools such as nut (git clone https://github.com/blawar/nut) also put a copy of the prod.keys you dumped earlier into the folder you just git cloned.
7. pip install -r requirements.txt (on linux) // python -m pip install requirements.txt (on windows)
8. python nut.py --organize-ncas C:/path/to/13.0.0/system/files/  /// /path/to/1300/nca-files (the folder that has the ncas)
9. you should now have the system firmware files organized by titleid in the folder you had them in.
10. for this example we will use "010000000000000F", "nifm". Proceed to open a terminal in that folder.
11. hactool --exefsdir=exefs b9aff2c32adc232047454512ae36b29c.nca exefsdir being wherever you want the exefs to go to. (the .nca name for this only applies for 13.0.0)
12. enter the output folder and run "hactool -t nso0 main --uncompressed uncompressed_main" - This accomplishes two things, one you get a decompressed version of the binary you are going to work on, and two it prints metadata such as the buildid which will be needed later on.
13. take note of the buildid that is output. (which is 8CB532EA199207191F04CE3DDECEC854C7CF07D6000000000000000000000000 in this example)
14. Open ghidra, make a new project where you want.
15. Click File -> import file -> Select uncompressed_main that you just decompressed (make certain it says the format is Nintendo Switch Binary)
![alt text](https://github.com/borntohonk/patches/blob/master/img/ghidra-nso.png?raw=true)
16. Click the dragon to open the ghidra CodeBrowser.
17. Click File -> open uncompressed_main (that you added to the project)
18. Click yes to analyze, and tick the switch-ipc option, then click analyze. Then let the process run until completed.

*For this specific example the intent is to make a function that otherwise usually looks for X-Organization: Nintendo to be true, if it does not find it to be true your wifi/lan adapter is disabled. We're going to make it do the opposite.

20. To find this offset of the function, you can look at the symbol tree, then NameSpaces, One of the SwitchD_XXXXXX numbers will look like this. (see picture)

![alt text](https://github.com/borntohonk/patches/blob/master/img/ghidra-nifm-offset.png?raw=true)

21. The patch we want to make is to change change out the instruction at that offset, with "MOV X0, XZR" + "RET" (E0 03 1F AA C0 03 5F D6)

![alt text](https://github.com/borntohonk/patches/blob/master/img/ghidra-nifm-after.png?raw=true)

22. To use this patch on the switch, you're going to want to save "50 41 54 43 48 01 08 14 00 08 E0 03 1F AA C0 03 5F D6 45 4F 46" as 8CB532EA199207191F04CE3DDECEC854C7CF07D6.ips (the build id that you got earlier) "50 41 54 43 48" is "PATCH", "01 08 14" is the offset we're patching, "00 08" is the length of patch we're applying, "E0 03 1F AA C0 03 5F D6" Is the patch we are applying at that offset (MOV X0, XZR" and "RET"), and 45 4F 46 is EOF. This effectively patches out the "connectivity test" and lets you use network functionality on closed networks where otherwise X-Organization: Nintendo would never be returned to the console.
23. You should now have a functional patch for nifm, and it can be used with Atmosphere by putting it into /atmosphere/exefs_patches/nifm_ctest/8CB532EA199207191F04CE3DDECEC854C7CF07D6.ips