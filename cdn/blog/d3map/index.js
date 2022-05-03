function map(mapdata) {
  const width=975,
    height=610;

  // Create an svg element to hold our map, and set it to the proper width and
  // height. The viewBox is set to a constant value becase the projection we're
  // using is designed for that viewPort size:
  // https://github.com/topojson/us-atlas#us-atlas-topojson
  const svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, 975, 610])
      .attr("style", "width: 100%; height: auto; height: intrinsic;");

  // Create the US boundary
  const usa = svg
    .append('g')
    .append('path')
    .datum(topojson.feature(mapdata, mapdata.objects.nation))
    .attr('d', d3.geoPath())

  // Create the state boundaries. "stroke" and "fill" set the outline and fill
  // colors, respectively.
  const state = svg
    .append('g')
    .attr('stroke', '#444')
    .attr('fill', '#eee')
    .selectAll('path')
    .data(topojson.feature(mapdata, mapdata.objects.states).features)
    .join('path')
    .attr('vector-effect', 'non-scaling-stroke')
    .attr('d', d3.geoPath());
}

window.addEventListener('DOMContentLoaded', async (event) => {
  const res = await fetch(`https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json`)
  const mapJson = await res.json()
  map(mapJson)
});
