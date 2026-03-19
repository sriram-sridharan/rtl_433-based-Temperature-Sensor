# YATS - Yet Another Temperature Sensor Using rtl_433

![CI](https://github.com/sriram-sridharan/rtl_433-based-Temperature-Sensor/actions/workflows/ci.yml/badge.svg)

I got bored with creating wireless temperature sensors with ESP8266s, so I started looking for cooler projects in a similar vein. A few weeks ago, I came across a project called [rtl_433](https://github.com/merbanan/rtl_433) that uses [rtl_sdr](http://sdr.osmocom.org/trac/wiki/rtl-sdr) to decode certain wireless signals sent over the 433MHz ISM band.

I'd previously seen references to rtl_sdr but did not pay much attention to the project. With the help of [RTL-SDR.com](https://www.rtl-sdr.com) and the [RTLSDR subreddit](https://www.reddit.com/r/RTLSDR/ "RTLSDR subreddit") I started digging into both projects and began my journey.

The goal of this project is simple: take temperature and humidity data from a commercially available sensor, decode it and send it to a PRTG installation for storage and visualization.

**2025 Update**: This project is now fully dockerized! No manual compilation, dependency management or driver blacklisting required. Just build the image, deploy it and you're on your way!

## Getting Started

- rtl_sdr compatible dongle with an appropriate antenna- I bought the [NooElec NESDR SMArt](https://smile.amazon.com/NooElec-NESDR-SMArt-Bundle-R820T2-Based/dp/B01GDN1T4S/ "NooElec NESDR SMArt") because it came with a 433MHz antenna (although a collapsible one will work just fine as well). [Here](http://www.radioforeveryone.com/p/july-6-2016-chinese-versus-branded.html "Here") is an article that might help you decide on a dongle.
- Temperature sensors - I bought [this one](https://smile.amazon.com/AcuRite-06002M-Wireless-Temperature-Humidity/dp/B00T0K8NXC/ "this one") but you can get any sensor that uses a protocol supported by [rtl_433](https://github.com/merbanan/rtl_433/blob/master/README.md "rtl_433").

### Prerequisites

- A [PRTG](https://www.paessler.com/prtg "PRTG") install - you can likely adapt this process to other similar monitoring systems
- Docker

### Components

- `config.ini` - Configuration file that stores your sensor IDs and PRTG URL
- `Dockerfile` - Think of this as a recipe to create a docker image. A cup of `hertzg/rtl_433:latest`, a tbsp of `python3`, a tsp of `temp_simplified.py` and a dash of `config.ini` is what lets you build the docker image locally with all the latest changes!
- `temp.sh` - This shell script contains the default command to be run when the image is started
- `temp_simplified.py` -  This is the python script that takes the climate data from `rtl_433` and sends it to PRTG

### Prep

Rename `config.ini.bak` to `config.ini`, add your sensor IDs and PRTG installation URL

### Build

- Building the image is easy: `docker build -t 433-temp:latest .`
- If you use Docker Hub or a similar registry, you can tag the image like so: `docker build -t username/433-temp:latest .`
- You can force download the latest version of all dependencies by using the `--no-cache` flag.
- Finally, you can push the freshly built image to your registry with: `docker push username/433-temp:latest`

## Deploy

The recommended way to run this container is via Docker Compose. I use this:

```yaml
433_temp:
  container_name: 433_temp
  # this is your username from the previous section
  image: username/433-temp:latest
  restart: always
  logging:
    options:
      max-size: "10m"
      max-file: "3"
  devices:
    - /dev/bus/usb:/dev/bus/usb
  environment:
    # Optional: pin to a specific RTL-SDR dongle by serial number.
    # Useful when multiple dongles are present (e.g. one for ADS-B, one for 433MHz).
    # Omit or leave blank to use the first available device.
    - RTL_SERIAL=1337
  healthcheck:
    # temp_simplified.py writes a heartbeat to /dev/shm (RAM) each time a reading is successfully processed
    # /dev/shm is used to avoid unnecessary writes to the host SSD.
    test: ["CMD-SHELL", "find /dev/shm/433_healthy -mmin -5 2>/dev/null | grep -q . || exit 1"]
    interval: 2m
    timeout: 10s
    retries: 3
    # allow time for the SDR dongle to initialize
    start_period: 2m
```

I pair this healthcheck with [willfarrell/autoheal](https://github.com/willfarrell/autoheal) to automatically restart unhealthy containers. If you do this, don't forget to add `labels: ["autoheal=true"]` to the `433_temp` service.

## Testing

Unit tests cover the XML payload builder and HTTP retry logic. You need to install [pytest](https://pytest.org) first:
```bash
pip3 install pytest
```
Note: You may need to do this in a `venv`.
  
Once this is done, you can run the tests:
```bash
python3 -m pytest tests/ -v
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Thanks

* [rtl_sdr project](https://osmocom.org/projects/sdr/wiki/rtl-sdr)
* [rtl_433 project](https://github.com/merbanan/rtl_433/)
* [r/RTLSDR](https://www.reddit.com/r/RTLSDR/)