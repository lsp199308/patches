#!/bin/bash
cd $HOME/ &&
wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.12%2B7/OpenJDK11U-jdk_x64_linux_hotspot_11.0.12_7.tar.gz &&
mkdir ojdk11 &&
tar xvzf OpenJDK11U-jdk_x64_linux_hotspot_11.0.12_7.tar.gz -C ojdk11 &&
rm OpenJDK11U-jdk_x64_linux_hotspot_11.0.12_7.tar.gz &&
export JAVA_HOME=$HOME/ojdk11/jdk-11.0.12+7 &&
export PATH="$HOME/ojdk11/jdk-11.0.12+7/bin:$PATH" &&
echo "export PATH="$HOME/ojdk11/jdk-11.0.12+7/bin:$PATH"" >> $HOME/.profile &&
echo "alias ghidra=~/ghidra/ghidra_10.0.3_PUBLIC/ghidraRun" >> $HOME/.bash_aliases
wget $(curl -s https://api.github.com/repos/NationalSecurityAgency/ghidra/releases/latest | grep "browser_download_url" | cut -d '"' -f 4) -O ghidra.zip &&
unzip ghidra.zip -d ghidra &&
rm ghidra.zip &&
export GHIDRA_INSTALL_DIR=$HOME/ghidra/ghidra_10.0.3_PUBLIC &&
git clone https://github.com/Adubbz/Ghidra-Switch-Loader &&
cd Ghidra-Switch-Loader &&
chmod +x gradlew &&
./gradlew &&
cd dist &&
unzip *.zip -d "$HOME/ghidra/ghidra_10.0.3_PUBLIC/Ghidra/Extensions" &&
cd ../.. &&
rm -rf Ghidra-Switch-Loader &&
source $HOME/.profile &&
source $HOME/.bash_aliases &&
ghidra