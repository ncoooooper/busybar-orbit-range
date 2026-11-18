"""Topocentric range from JPL Horizons or a public satellite element set."""
import csv,io,json,datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from serve import page
INTERVAL=60
def snapshot(o,m):
    lat,lon,alt=[float(o.get(k,0)) for k in ("latitude","longitude","altitude_m")]
    now=datetime.datetime.now(datetime.timezone.utc)
    if o.get("catalog_id"):
        from skyfield.api import EarthSatellite,load,wgs84
        sat=int(o["catalog_id"])
        if (now.timestamp()-m.get("fetched",0))>3600:
            def pair(lines):
                for i,line in enumerate(lines[:-1]):
                    if line.startswith("1 ") and line[2:7].strip()==str(sat) and lines[i+1].startswith("2 ") and line[2:7]==lines[i+1][2:7]:
                        return line,lines[i+1]
                raise ValueError("Catalog ID absent from element set")
            if o.get("tle_file"):
                one,two=pair(Path(o["tle_file"]).expanduser().read_text().splitlines())
            else:
                urls=[f"https://celestrak.org/NORAD/elements/gp.php?CATNR={sat}&FORMAT=TLE"]
                if sat==25544:urls.append("https://www.amsat.org/tle/current/nasabare.txt")
                for url in urls:
                    try:
                        with urlopen(url,timeout=8) as r:one,two=pair(r.read().decode().splitlines())
                        break
                    except (OSError,ValueError):
                        if url==urls[-1]:raise
            m["timescale"]=load.timescale()
            m["sat"]=EarthSatellite(one,two,str(sat),m["timescale"]);m["fetched"]=now.timestamp()
        body=m["sat"]
        if abs((now-body.epoch.utc_datetime()).total_seconds())>7*86400:raise ValueError("Satellite elements are over seven days old")
        km=(body-wgs84.latlon(lat,lon,elevation_m=alt)).at(m["timescale"].from_datetime(now)).distance().km
        source="SGP4 orbital estimate"
    else:
        q=dict(format="json",COMMAND=o.get("target","499"),OBJ_DATA="NO",MAKE_EPHEM="YES",EPHEM_TYPE="OBSERVER",CENTER="coord@399",COORD_TYPE="GEODETIC",SITE_COORD=f"{lon},{lat},{alt/1000}",TLIST=f"{now.timestamp()/86400+2440587.5:.8f}",QUANTITIES="20",CSV_FORMAT="YES",RANGE_UNITS="KM")
        with urlopen("https://ssd.jpl.nasa.gov/api/horizons.api?"+urlencode({k:v if k=="format" else "'"+str(v)+"'" for k,v in q.items()}),timeout=14) as r:response=json.load(r)
        result=response["result"]
        if "$$SOE" not in result:raise ValueError("No ephemeris. Select a unique Horizons record or a comet designation with CAP.")
        part=result.split("$$SOE")[1].split("$$EOE")[0].strip()
        cells=next(csv.reader(io.StringIO(part)));numbers=[float(v) for v in cells[3:] if v.strip()]
        km=numbers[0];source="JPL observer range"
    value=f"{km/1e6:.2f}M km" if km>=1e6 else f"{round(km)} km"
    return dict(state=source,key=str(round(km)),pages=[page("DISTANCE",value,o["name"],source,"Observer to object"),page("OBSERVER",f"{lat:g}",f"Longitude {lon:g}",f"Elevation {alt:g} m",now.strftime("%H:%M UTC"))])
