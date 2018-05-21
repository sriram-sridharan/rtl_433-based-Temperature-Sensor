# YATS - Yet another temperature sensor using rtl_433

I got bored with creating wireless temperature sensors with ESP8266s, so I started looking for cooler projects on a similar vein. A few weeks ago, I came across a project called [rtl_433](https://github.com/merbanan/rtl_433) that uses [rtl_sdr](http://sdr.osmocom.org/trac/wiki/rtl-sdr) to decode certain wireless signals sent over the 433MHz ISM band.

I had previously seen references to rtl_sdr but did not pay much attention to the project. With the help of [RTL-SDR.com](https://www.rtl-sdr.com) and the [RTLSDR subreddit](https://www.reddit.com/r/RTLSDR/ "RTLSDR subreddit") I started reading up on both these projects and began my journey.

The goal of this project is simple - take temperature and humidity data from a commercially available sensor, decode it and send it to a PRTG installation for storage and visualization.

## Getting Started

- A Raspberry Pi - I used a Raspberry Pi 3 Model B that I bought from Microcenter to use with the [AIY Voice Kit](https://aiyprojects.withgoogle.com/voice/ "AIY Voice Kit").
- A micro-USB cable and a USB power supply (to power the Raspberry Pi and SDR dongle) - I used a OEM HTC charger that can do 2.4A but something [like this](https://www.raspberrypi.org/products/raspberry-pi-universal-power-supply/ "like this") would be the best.
- A microSD card (at least 8GB) loaded with a \*nix based OS  - I used Raspbian Stretch
- rtl_sdr compatible dongle with appropriate antenna- I bought the [NooElec NESDR SMArt](https://smile.amazon.com/NooElec-NESDR-SMArt-Bundle-R820T2-Based/dp/B01GDN1T4S/ "NooElec NESDR SMArt") because it came with a 433MHz antenna (although a collapsible one will work just fine as well). [Here](http://www.radioforeveryone.com/p/july-6-2016-chinese-versus-branded.html "Here") is an article that might help you decide on a dongle.
- Temperature sensors - I bought [this one](https://smile.amazon.com/AcuRite-06002M-Wireless-Temperature-Humidity/dp/B00T0K8NXC/ "this one") but you can get any sensor that uses a protocol supported by [rtl_433](https://github.com/merbanan/rtl_433/blob/master/README.md "rtl_433").

### Prerequisites

- A [PRTG](https://www.paessler.com/prtg "PRTG") install - you can likely adapt this process to other similar monitoring systems
- Python 2.x (comes installed on Raspbian) - the script is untested on Python 3 and I understand that there are some differences in urllib behaviour between the two versions

### Installing

#### Prepwork
First update and upgrade all installed packages
```Shell
sudo apt update
sudo apt upgrade
```
Then plug in your rtl_sdr dongle and check to see if it is detected
```Shell
lsusb
```
You should see something like `Bus 001 Device 004: ID 0bda:2838 Realtek Semiconductor Corp. RTL2838 DVB-T`

Now check to see if dvb drivers are automatically loaded
```Shell
lsmod | grep dvb
```
If you see something like `dvb_usb_rtl28xxu`, that means that the default dvb drivers were installed and loaded. If that is the case, blacklist it by editing `/etc/modprobe.d/blacklist-dvb.conf`
```Shell
sudo nano /etc/modprobe.d/blacklist-dvb.conf
```
and adding `blacklist dvb_usb_rtl28xxu` to the file. If you're using nano to edit the file, like in my example, `ctrl-x` to get the save dialog and then hit `Y`.

#### Installing rtl_sdr
rtl_sdr has a few dependencies which may or may not be installed on your OS. Here are the dependencies in case they are not: `git-core`, `git`, `cmake`, `build-essential`, `libusb-1.0.0-dev`

Now download rtl_sdr via git (I am assuming you are doing this in your home directory or you will need to modify step 8) and compile it.
```Shell
git clone git://git.osmocom.org/rtl-sdr.git
mkdir build
cd build/
cmake ../ -DINSTALL_UDEV_RULES=ON
make
sudo make install
sudo ldconfig
cd ~
sudo cp ./rtl-sdr/rtl-sdr.rules /etc/udev/rules.d/
```
Now, reboot using `sudo shutdown -r now`.

After rebooting use `rtl_test` to see if your rtl_dongle is detected properly and functioning normally.

#### Installing rtl_433

Simply follow [this well writted readme](https://github.com/merbanan/rtl_433/blob/master/README.md "this well writted readme") to install rtl_433.

Okay, now let us test the whole set up so far. Mount the 433MHz antenna or collapse your telescopic antenna to quarter wavelength (~17.2cm, there's no need to be super precise). Now, run `rtl_433 -G`. This command will basically run through all supported protocols and try decode the received transmissions.

You'll likely see something like [this](https://gist.github.com/sriram-sridharan/4da51490ebdbf512c3a9b9c18fb8d5cd "this") if you have one or more sensors operational (see the Prerequisites section). 

We are going to use the HTTP Push Data Advanced sensor in PRTG to receive the data. [Here](https://www.paessler.com/manuals/prtg/http_push_data_advanced_sensor) is the documentation for this sensor. This sensor accepts data encoded in xml or json formats and sent via HTTP GET and POST requests. We will use xml encoding to send the data via HTTP GET requests. I use one PRTG sensor with two channels (temperature and humidity) for each temperature sensor although you could definitely bunch multiple temperature sensors into one PRTG sensor with the only downside being a more complicated graph. You can use a single port for PRTG to listen to pushed data across multiple PRTG sensors but remember that this port will need to be different from the port that PRTG runs on (obvious but I thought I should note this).

I would also suggest creating an [IFTTT webhook applet](https://ifttt.com/maker_webhooks) to get notified of issues with either the USB tuner or the sensors themselves.

Finally, download my repo `git clone git@github.com:sriram-sridharan/rtl_433-based-Temperature-Sensor.git` and edit the configuration section of `main.py` with your settings and tokens.

You can use [this guide](https://www.raspberrypi.org/documentation/linux/usage/rc-local.md) to make the script auto-run at boot.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Thanks

* [rtl_sdr project](https://osmocom.org/projects/sdr/wiki/rtl-sdr)
* [rtl_433 project](https://github.com/merbanan/rtl_433/)
* [r/RTLSDR](https://www.reddit.com/r/RTLSDR/)