import { extent, max, min } from "d3-array";
import { json } from "d3-fetch";
import { scaleLog } from "d3-scale";
import { interpolateBlues } from "d3-scale-chromatic";
import { select, pointer } from "d3-selection";
import { format } from "d3-format";

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

function makeUSMap(target, populationData) {
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

  // add population data to the state objects
  Object.values(states).forEach(s => s.population = populationData[s.name]);

  const svg = select(target)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "width: 100%; height: auto; height: intrinsic;");

  const statesg = svg
    .append("g")
    .selectAll("g")
    .data(Object.values(states))
    .join("g")
    .attr("class", "state");
  statesg
    .append("rect")
    .attr("x", (d) => d.x * (squareSize + padding * 2))
    .attr("y", (d) => d.y * (squareSize + padding * 2))
    .attr("width", squareSize)
    .attr("height", squareSize)
    .attr("state", (d) => d.name)
    .attr("fill", (d) => colorScale(d.population));
  statesg
    .append("text")
    .attr("x", (d) => d.x * (squareSize + padding * 2) + squareSize / 2)
    .attr("y", (d) => d.y * (squareSize + padding * 2) + squareSize / 2)
    .attr("fill", "white")
    .style("text-anchor", "middle")
    .attr("dominant-baseline", "central")
    .text((d) => d.key);

  return svg;
}

pop_prom = json(
  `https://cdn.billmill.org/static/blog/us_choro/population.json`
);

function onready(f) {
  if (document.readyState !== "loading") {
    f();
  } else {
    window.addEventListener("DOMContentLoaded", f);
  }
}

onready(async (event) => {
  const popData = await pop_prom;

  // Map 1: add <title> elements to each state
  const map1 = makeUSMap("#map", popData);
  let states = map1.selectAll("g.state");
  states.append("title").text((d) => d.name);

  // Map 2: add SVG tooltips
  const map2 = makeUSMap("#map2", popData);
  const tooltip = map2
    .append("g")
    .attr("class", "tooltip")
    .style("pointer-events", "none");

  states = map2.selectAll("g.state")
    .on("pointerenter pointermove", (evt) => {
      // get the SVG coordinates of the pointer event
      [mouseX, mouseY] = pointer(evt);

      // get the state data and generate a message to display. Format the
      // number nicely
      const target = select(evt.target).datum(),
        name = target.name,
        pop = target.population,
        msg = `${name}\npopulation: ${format(",")(pop)}`,
        padding = 4;

      // re-display the tooltip if it was hidden
      tooltip.style("display", null);

      // Create a rectangle to serve as the tooltip background - we will set
      // its height and width later, after we have created the tooltip text and
      // can get its width. We need to add it to the SVG first so that it gets
      // displayed behind the tooltip
      const bg = tooltip
        .selectAll("rect")
        .data([,])
        .join("rect")
        .attr("fill", "#ffffff")
        .attr("fill-opacity", "0.9");

      // Create the tooltip text element. We use multiple <tspan> elements
      // because SVG text elements do not support line breaks, so each line of
      // text gets a separate <tspan> within the <text> element
      const txt = tooltip
        .selectAll("text")
        .data([,])
        .join("text")
        .attr("dominant-baseline", "central")
        .call(text => text.selectAll("tspan")
          .data(msg.split(/\n/))
          .attr("fill", "black")
          .style("text-anchor", "middle")
          .join("tspan")
            .attr("x", mouseX)
            .attr("y", (_, i) => mouseY + 30*i)
            .text(d => d))

      // Get the bounding box of the text node we created, and set the
      // background rectangle's size appropriately
      const bbox = txt.node().getBBox(),
        width = bbox.width + padding * 2,
        height = bbox.height + padding * 2;
      bg.attr("height", height)
        .attr("width", width)
        .attr("x", mouseX - (width/2))
        .attr("y", mouseY - (height/4));
    })
    .on("pointerleave", (evt) => {
      // hide the tooltip
      tooltip.style("display", "none");
    })
    .on("touchstart", (evt) => evt.preventDefault());

  const map3 = makeUSMap("#map3", popData);
  const tooltipdiv = select("#map3")
    .append("div")
    .attr("class", "tooltip")
    .style("display", "none")
    .style("background", "rgba(69,77,93,.9)")
    .style("border-radius", ".2rem")
    .style("color", "#fff")
    .style("padding", ".6rem")
    .style("position", "absolute")
    .style("text-overflow", "ellipsis")
    .style("white-space", "pre")
    .style("line-height", "1em")
    .style("z-index", "300");

  states = map3.selectAll("g.state")
    .on("pointerenter pointermove", (evt) => {
      const target = select(evt.target).datum();
      tooltipdiv
        .style("display", null)
        .html(`${target.name}<br>population: ${format(",")(target.population)}`)
        .style("top", evt.pageY - 10 + "px")
        .style("left", evt.pageX + 10 + "px");
    })
    .on("pointerleave", (evt) => {
      // hide the tooltip
      tooltipdiv.style("display", "none");
    })
});

