sed -i 's/^blacklist 12c-bcm2708/#blacklist 12c-bcm2708/'       /etc/modprobe.d/raspi-blacklist.conf
sed -i 's/^blacklist snd-soc-pcm512x/#snd-soc-pcm512x/'         /etc/modprobe.d/raspi-blacklist.conf
sed -i 's/^blacklist snd-soc-wm8804/#blacklist snd-soc-wm8804/' /etc/modprobe.d/raspi-blacklist.conf
sudo cp ../misc/asound.conf /etc/asound.conf
sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' /boot/config.txt
sudo echo "" >> /boot/config.txt

if (grep -Fxq "dtoverlay=hifiberry-dac" /boot/config.txt)
then
   sed -i 's/^#dtoverlay=hifiberry-dac/dtoverlay=hifiberry-dac/' /etc/modprobe.d/raspi-blacklist.conf
else
   sudo echo "dtoverlay=hifiberry-dac" >> /boot/config.txt
fi   
if (grep -Fxq "dtoverlay=i2s-mmap" /boot/config.txt)
then
    sed -i 's/^#dtoverlay=i2s-mmap/dtoverlay=i2s-mmap/' /etc/modprobe.d/raspi-blacklist.conf
else
   sudo echo "dtoverlay=i2s-mmap" >> /boot/config.txt
fi    
