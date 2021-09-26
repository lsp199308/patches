Part 1B: Setting up Ghidra

This guide is done on Ubuntu, and assumes you have git, wget and curl. They can be gotten by doing "sudo apt-get install -y wget curl git"

1. Get openjdk 11 lts from https://adoptium.net/ (cd ~ && wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.12%2B7/OpenJDK11U-jdk_x64_linux_hotspot_11.0.12_7.tar.gz)
2. Extract openjdk that you just downloaded (cd ~ && mkdir ojdk11 && tar xvzf OpenJDK11U-jdk_x64_linux_hotspot_11.0.12_7.tar.gz -C ~/ojdk11)
3. Set enviroment variable for JAVA_HOME (export JAVA_HOME=~/ojdk11/jdk-11.0.12+7) add this to .bashrc or .profile.
4. Get ghidra (cd ~ && wget $(curl -s https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/latest | grep "browser_download_url" | cut -d '"' -f 4) -O ~/ghidra.zip )
4. Extract it (unzip ~/ghidra.zip -d ~/ghidra)
5. Set enviroment variable GHIDRA_INSTALL_DIR, in current scheme it should be whichever folder is extracted to inside of ~/ghidra/ghidra_xx.x.x_PUBLIC "export GHIDRA_INSTALL_DIR=~/ghidra/ghidra_10.0.3_PUBLIC" without quotations into your terminal.
5. Clone the switch loader repository with "cd ~ && git clone https://github.com/Adubbz/Ghidra-Switch-Loader"
6. Run gradlew in the Ghidra-Switch-Loader directory by doing "cd ~/Ghidra-Switch-Loader && chmod +x gradlew && ./gradlew" in your terminal.
7. Run ghidra that you should have set up in the previous steps (cd ~/ghidra/ghidra_10.0.3_PUBLIC/ghidraRun) Agree/accept to the prompt.
8. Click "File" top left then "Install extensions"
9. Press the + button in upper right corner.
10. Navigate to your Ghidra-Switch-Loader directory and then into the "dist" folder it made, then select the .zip that should be in there.
11. Restart ghidra by using .ghidraRun in the ghidra folder (or set just do "alias ghidra=~/ghidra/ghidra_10.0.3_PUBLIC/ghidraRun" and also add it to .profile or .bashrc and then just do "ghidra" in the terminal)
12. You should now have ghidra running with the Nintendo Switch Loader.

![alt text](https://github.com/borntohonk/patches/blob/master/img/ghidra-l.png?raw=true)