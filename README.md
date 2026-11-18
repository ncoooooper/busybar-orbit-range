# Orbit Range

Read the line-of-sight distance from your observing location to a celestial target or satellite. A satellite directly over your city and one below the horizon can have very different ranges even at the same orbital altitude.

## Setup

Set `latitude`, `longitude` and `altitude_m` for the observer. The default selects Mars with Horizons ID `499`. Use `301` for the Moon or a specific small-body designation such as `DES=1P;CAP;` for Halley, and update `name`. Resolve ambiguous object names in JPL Horizons first. For the ISS, remove `target`, add `"catalog_id":25544`, set `name` to `ISS` and install `companion/requirements-satellite.txt`. Satellite mode uses public CelesTrak elements, refreshes them hourly, and rejects elements over seven days old. If CelesTrak is unavailable, the ISS example also checks the AMSAT element bulletin. To use a downloaded element file, keep `catalog_id` and set `tle_file` to its local path.

From the repository root, copy the example and start the companion with Python 3.10 or newer.

```sh
cp companion/example.json config.json
# Edit config.json for your source before starting the server.
python3 companion/serve.py --config config.json
```

In the emulator, run `~/.busy-emulator/bin/busy-emulator allow-local 8770` and approve that port. Open **Apps → Orbit Range → Setup**, set **Local companion URL** to `http://127.0.0.1:8770/reading`, save, then reopen the app. For a physical bar, start the companion with `--host YOUR_LAN_IP` and replace `127.0.0.1` with that address. Bind only to your trusted network. Open `/reading` on the host to inspect the current reading. Keep credentials in the host environment.

## Read an observer range

Open DISTANCE. The rear identifies the object and calculation source. Distances over one million kilometers use M km. The sample illustrates a 705 km ISS range. It represents one viewing geometry.

![The example changes from a 705 km ISS range to its observer latitude.](media/guide/use-1.gif)

## Change observing location

Turn to OBSERVER and check latitude, longitude and elevation. To move the observer, change the config and restart the companion. Click the wheel to sync, then turn back to DISTANCE. Values are calculated slant ranges and change with time.

![The observer coordinates give way to the range page.](media/guide/use-2.gif)

## Run in the emulator

Install BUSY Bar Emulator and open it. From this repository run the following command, then press **Back** when you finish.

```sh
~/.busy-emulator/bin/busy-emulator dev --once
```

The recordings use example responses on emulator firmware. Each display pixel is enlarged to a 9 × 9 square.

[JPL Horizons API](https://ssd-api.jpl.nasa.gov/doc/horizons.html) · [CelesTrak orbital elements](https://celestrak.org/NORAD/elements/) · [Skyfield satellite positions](https://rhodesmill.org/skyfield/earth-satellites.html).

[Rear display](screenshots/back-1.png) · [MIT license](LICENSE)
