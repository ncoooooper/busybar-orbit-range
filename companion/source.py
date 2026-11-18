"""Topocentric range from JPL Horizons or a public satellite element set."""
import csv,io,json,datetime
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
            with urlopen(f"https://celestrak.org/NORAD/elements/gp.php?CATNR={sat}&FORMAT=TLE",timeout=10) as r:lines=r.read().decode().strip().splitlines()
            one=next(x for x in lines if x.startswith("1 "));two=next(x for x in lines if x.startswith("2 "))
            m["sat"]=EarthSatellite(one,two,str(sat),load.timescale());m["fetched"]=now.timestamp()
        body=m["sat"]
        if abs((now-body.epoch.utc_datetime()).total_seconds())>7*86400:raise ValueError("Satellite elements are over seven days old")
        km=(body-wgs84.latlon(lat,lon,elevation_m=alt)).at(body.ts.from_datetime(now)).distance().km
        source="SGP4 orbital estimate"
    else:
        q=dict(format="json",COMMAND=o.get("target","499"),OBJ_DATA="NO",MAKE_EPHEM="YES",EPHEM_TYPE="OBSERVER",CENTER="coord@399",COORD_TYPE="GEODETIC",SITE_COORD=f"{lon},{lat},{alt/1000}",TLIST=f"{now.timestamp()/86400+2440587.5:.8f}",QUANTITIES="20",CSV_FORMAT="YES",RANGE_UNITS="KM")
        with urlopen("https://ssd.jpl.nasa.gov/api/horizons.api?"+urlencode({k:v if k=="format" else "'"+str(v)+"'" for k,v in q.items()}),timeout=14) as r:response=json.load(r)
        result=response["result"];part=result.split("$$SOE")[1].split("$$EOE")[0].strip()
        cells=next(csv.reader(io.StringIO(part)));numbers=[float(v) for v in cells[3:] if v.strip()]
        km=numbers[0];source="JPL observer range"
    value=f"{km/1e6:.2f}M km" if km>=1e6 else f"{round(km)} km"
    return dict(state=source,key=str(round(km)),pages=[page("DISTANCE",value,o["name"],source,"Observer to object"),page("OBSERVER",f"{lat:g}",f"Longitude {lon:g}",f"Elevation {alt:g} m",now.strftime("%H:%M UTC"))])
