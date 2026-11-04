# OSM2VISSIM – Import OpenStreetMap into PTV VISSIM

A Python script that converts an OpenStreetMap (`.osm`) extract into a PTV VISSIM network (`.inpx`) through the VISSIM COM interface. The generated network is in true metres and is pinned to VISSIM's background map, so it lines up with the base map without manual moving.

This repository is a fork of [bmetrafficlab/OSM2VISSIM](https://github.com/bmetrafficlab/OSM2VISSIM) (BME Road Traffic Control Laboratory, MIT licence). This version changes how network coordinates and the map reference point are computed.

## What it creates

| OSM data | VISSIM object |
|---|---|
| Ways tagged `highway=*` (roads, service roads, cycleways, footways, steps) | Links |
| `lanes`, `lanes:forward/backward`, `turn:lanes:*`, `oneway`, `junction` tags | Lane counts and a second link in the opposite direction |
| Ways that share a node | Connectors |
| `traffic_signals` nodes | Signal controllers, signal groups and signal heads |
| `restriction` relations (`no_left_turn`, `no_right_turn`, `only_*`) | Connectors that are skipped or enforced |

Lane widths: car links 3.5 m (2.75 m for single-lane two-way roads), cycleways 1.5 m, footways and steps 1 m.

## Requirements

- Windows (the script uses `pywin32` to talk to VISSIM)
- PTV VISSIM 2026 installed and licensed (the script calls `Vissim.Vissim.26`; edit that line for another version)
- Python 3 with:
  - `pywin32`
  - `GDAL` / `osgeo` built with the OSM driver
  - `shapely`
  - `tkinter` (included with standard Python)

## How to use

1. Export an area from [openstreetmap.org](https://www.openstreetmap.org/) (Export → `.osm`) and save it in the same folder as the script, for example `Model 1.osm`.
2. Open a terminal in that folder and run:
   ```
   python OSM2VISSIM_v0.1.py
   ```
3. In the small window, type the file name **without** `.osm` (for example `Model 1`) and click **Set**.
4. Wait for the console to report `Creating links`, `Creating signal heads` and the connector progress, ending at `100.0%`. VISSIM opens during the run and must not be closed.
5. The script saves `<name>.inpx` in the current folder and reloads it in VISSIM. Turn on the background map in VISSIM (Base Data → Background Maps) to see the network on top of the map.

Outputs: `<name>.inpx` is the network, and `<name>.osm.inpx` is a temporary empty file the script uses to start a clean network.

## Methodology

### 1. Local projection for network coordinates

VISSIM network coordinates are metres, so the script needs distances that are true on the ground. Earlier versions used Web Mercator directly, which stretches distances by 1/cos(latitude) (about 1.6× at London's latitude).

The script instead:

1. Reads the centre of the OSM `<bounds>` element, or the centre of all node coordinates if there are no bounds.
2. Builds a local Transverse Mercator projection centred on that point (`+proj=tmerc +k=1 +units=m`).
3. Projects every way vertex into that projection (function `Convert_to_mercator`, name kept from the original).

The centre of the area therefore becomes (0, 0) in VISSIM, and link lengths are true metres.

### 2. Pinning the network to VISSIM's background map

After saving, the script edits the `refPointMap` and `refPointNet` entries in the `.inpx` file:

- `refPointNet` = (0, 0), the network origin.
- `refPointMap` = the same point (the OSM bounds centre) in VISSIM's map coordinates.

VISSIM's map is a spherical Mercator with Earth radius **6,371,000 m**, not the 6,378,137 m used by EPSG:3857 / Web Mercator. Using EPSG:3857 shifts the reference point by about 7.5 km in y at latitude 51.5°, so the script computes the map point directly:

```
x = R · lon                       (radians)
y = R · ln( tan( π/4 + lat/2 ) )  with R = 6,371,000 m
```

VISSIM applies the 1/cos(latitude) map scaling itself, so the true-metre network lines up with the map.

### 3. Links and lanes

Each OSM way is read through GDAL's OSM driver. The lane count and direction come from the OSM tags (`lanes:forward`, `lanes:backward`, `turn:lanes:*`, `lanes`, `oneway`). Two-way roads are created as one link plus an opposite-direction link; the opposite link gets a negative name (`-<way id>`). The OSM way id is stored in the link's `Name`.

### 4. Connectors

Ways that touch (shared OSM nodes) are recorded when they are read. For each pair, the script connects the end of one link to the nearest vertex of the other if it is within 5 m (3 m for links of 5 m or shorter). Connector positions are kept inside short links. Turn restrictions are applied here: `no_*` relations remove the connector and `only_*` relations keep only the allowed ones.

### 5. Signals

For each `traffic_signals` node on a way, the script finds the link direction that runs towards the node and places a signal head on every lane about 5 m before the stop line. Signal nodes within 30 m of each other share one signal controller, and each head gets its own signal group.

## Known limitations

- Windows only, and VISSIM must be installed.
- Only `highway=*` ways in the list in the script are imported.
- Signal timing is not created. The controllers and groups are empty.
- Large areas can take a long time because the connector search compares every link pair.
- Check the network in VISSIM afterwards. OSM tagging varies, and some junctions need manual clean-up.

## Licence

MIT, see [LICENSE.md](LICENSE.md). Original work © 2023 BME Road Traffic Control Laboratory.
