import { extent, max, min } from "d3-array";
import { json } from "d3-fetch";
import { scaleLog } from "d3-scale";
import { interpolateBlues } from "d3-scale-chromatic";
import { select } from "d3-selection";

states = {
  AK: { name: "Alaska", key: "AK" },
  ME: { name: "Maine", key: "ME" },
  VT: { name: "Vermont", key: "VT" },
  NH: { name: "New Hampshire", key: "NH" },
  MA: { name: "Massachusetts", key: "MA" },
  WA: { name: "Washington", key: "WA" },
  MT: { name: "Montana", key: "MT" },
  ND: { name: "North Dakota", key: "ND" },
  SD: { name: "South Dakota", key: "SD" },
  MN: { name: "Minnesota", key: "MN" },
  WI: { name: "Wisconsin", key: "WI" },
  MI: { name: "Michigan", key: "MI" },
  NY: { name: "New York", key: "NY" },
  CT: { name: "Connecticut", key: "CT" },
  RI: { name: "Rhode Island", key: "RI" },
  OR: { name: "Oregon", key: "OR" },
  ID: { name: "Idaho", key: "ID" },
  WY: { name: "Wyoming", key: "WY" },
  NE: { name: "Nebraska", key: "NE" },
  IA: { name: "Iowa", key: "IA" },
  IL: { name: "Illinois", key: "IL" },
  IN: { name: "Indiana", key: "IN" },
  OH: { name: "Ohio", key: "OH" },
  PA: { name: "Pennsylvania", key: "PA" },
  NJ: { name: "New Jersey", key: "NJ" },
  CA: { name: "California", key: "CA" },
  NV: { name: "Nevada", key: "NV" },
  UT: { name: "Utah", key: "UT" },
  CO: { name: "Colorado", key: "CO" },
  KS: { name: "Kansas", key: "KS" },
  MO: { name: "Missouri", key: "MO" },
  KY: { name: "Kentucky", key: "KY" },
  WV: { name: "West Virginia", key: "WV" },
  DC: { name: "District of Columbia", key: "DC" },
  MD: { name: "Maryland", key: "MD" },
  DE: { name: "Delaware", key: "DE" },
  AZ: { name: "Arizona", key: "AZ" },
  NM: { name: "New Mexico", key: "NM" },
  OK: { name: "Oklahoma", key: "OK" },
  AR: { name: "Arkansas", key: "AR" },
  TN: { name: "Tennessee", key: "TN" },
  VA: { name: "Virginia", key: "VA" },
  NC: { name: "North Carolina", key: "NC" },
  TX: { name: "Texas", key: "TX" },
  LA: { name: "Louisiana", key: "LA" },
  MS: { name: "Mississippi", key: "MS" },
  AL: { name: "Alabama", key: "AL" },
  GA: { name: "Georgia", key: "GA" },
  SC: { name: "South Carolina", key: "SC" },
  HI: { name: "Hawaii", key: "HI" },
  FL: { name: "Florida", key: "FL" },
};

grid = [
  ["AK", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "ME"],
  ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "  ", "VT", "NH"],
  ["  ", "WA", "ID", "MT", "ND", "MN", "IL", "WI", "MI", "CT", "MA", "RI"],
  ["  ", "OR", "NV", "WY", "SD", "IA", "IN", "OH", "PA", "NY", "NJ", "  "],
  ["  ", "CA", "UT", "CO", "NE", "MO", "KY", "WV", "VA", "MD", "DE", "  "],
  ["  ", "  ", "AZ", "NM", "KS", "AR", "TN", "NC", "SC", "DC", "  ", "  "],
  ["  ", "  ", "  ", "  ", "OK", "LA", "MS", "AL", "GA", "  ", "  ", "  "],
  ["HI", "  ", "  ", "  ", "TX", "  ", "  ", "  ", "  ", "FL", "  ", "  "],
];

function match(grid, states) {
  for (row = 0; row < grid.length; row++) {
    for (col = 0; col < grid[0].length; col++) {
      if (grid[row][col] !== "  ") {
        states[grid[row][col]].y = row;
        states[grid[row][col]].x = col;
      }
    }
  }
}
match(grid, states);

function map(populationData) {
  const width = 975,
    height = 610,
    padding = 2,
    scale = scaleLog()
      .domain(extent(Object.values(populationData)))
      .range([0.3, 1]),
    colorScale = (d) => interpolateBlues(scale(d)),
    cols = grid[0].length,
    rows = grid.length,
    squareSize = min([
      (width - cols * padding * 2) / cols,
      (height - rows * padding * 2) / rows,
    ]);

  const svg = select("#map")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "width: 100%; height: auto; height: intrinsic;");

  const statesg = svg
    .append("g")
    .selectAll("g")
    .data(Object.values(states))
    .join("g");
  statesg
    .append("rect")
    .attr("x", (d) => d.x * (squareSize + padding * 2))
    .attr("y", (d) => d.y * (squareSize + padding * 2))
    .attr("width", squareSize)
    .attr("height", squareSize)
    .attr("state", (d) => d.name)
    .attr("fill", (d) => colorScale(populationData[d.name]));
  statesg
    .append("text")
    .attr("x", (d) => d.x * (squareSize + padding * 2) + squareSize / 2)
    .attr("y", (d) => d.y * (squareSize + padding * 2) + squareSize / 2)
    .attr("fill", "white")
    .style("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .text((d) => d.key);
}

function onready(f) {
  if (document.readyState !== "loading") {
    f();
  } else {
    window.addEventListener("DOMContentLoaded", f);
  }
}

onready(async (event) =>
  map(
    await json(`https://cdn.billmill.org/static/blog/us_choro/population.json`)
  )
);
