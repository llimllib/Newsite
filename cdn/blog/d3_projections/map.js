import { extent } from "d3-array";
import { json } from "d3-fetch";
import { geoPath, geoAlbersUsa } from "d3-geo";
import { scaleLog } from "d3-scale";
import { interpolateGreys } from "d3-scale-chromatic";
import { select } from "d3-selection";
import { feature } from "topojson-client";

function map(mapData, populationData) {
  const width = 975,
    height = 610,
    scale = scaleLog().domain(extent(Object.values(populationData))),
    colorScale = (d) => interpolateGreys(scale(d)),
    projection = geoAlbersUsa().scale(1300).translate([487.5, 305]);

  const svg = select("#map")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, 975, 610])
    .attr("style", "width: 100%; height: auto; height: intrinsic;");

  const usa = svg
    .append("g")
    .append("path")
    .datum(feature(mapData, mapData.objects.nation))
    .attr("d", geoPath());

  const state = svg
    .append("g")
    .attr("stroke", "#444")
    .selectAll("path")
    .data(feature(mapData, mapData.objects.states).features)
    .join("path")
    .attr("fill", (d) => colorScale(populationData[d.properties.name]))
    .attr("vector-effect", "non-scaling-stroke")
    .attr("d", geoPath());
}

function onready(f) {
  if (document.readyState !== "loading") {
    f();
  } else {
    window.addEventListener("DOMContentLoaded", f);
  }
}

onready(async (event) => {
  map(
    ...(await Promise.all([
      // json(`https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json`),
      json(`https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json`),
      json(`https://cdn.billmill.org/static/blog/us_choro/population.json`),
    ]))
  );
});
