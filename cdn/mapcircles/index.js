window.data = {'ME': 2, 'MA': 34, 'VT': 22, 'NH': 10, 'CT': 12, 'RI': 10, 'NY': 30};

function map(data, mapdata) {
  const width=975,
    height=610,
    minRadius=5,
    maxRadius=15,
    radiusScale = d3.scaleLinear()
      .domain(d3.extent(Object.values(data)))
      .range([minRadius, maxRadius]);

  const projection = d3.geoAlbersUsa().scale(1300).translate([487.5, 305])

  const svg = d3.select("#map").append("svg")
      .attr("width", width)
      .attr("height", height)
      .attr("viewBox", [0, 0, width, height])
      .attr("style", "width: 100%; height: auto; height: intrinsic;");

  const g = svg.append('g')

  const usa = g
    .append('path')
    .datum(topojson.feature(mapdata, mapdata.objects.nation))
    .attr('fill', '#ddd')
    .attr('d', d3.geoPath())

  const state = g
    .append('g')
    .attr('stroke', '#444')
    .attr('fill', '#eee')
    .selectAll('path')
    .data(topojson.feature(mapdata, mapdata.objects.states).features)
    .join('path')
    .attr('vector-effect', 'non-scaling-stroke')
    .attr('d', d3.geoPath());

  const circles = svg.append('g')
  Object.keys(data).forEach(d => {
    if (STATES[d]) {
      const state = topojson.feature(us, "states").features.filter(s => s.properties.name == STATES[d]);
      const centroid = d3.geoPath().centroid(state[0]);
      console.log(d, data[d], radiusScale(data[d]), radiusScale);
      circles.append('circle')
        .attr("cx", centroid[0])
        .attr("cy", centroid[1])
        .attr("fill", "ddd")
        .attr("r", radiusScale(data[d]));
    }
  });
}

window.addEventListener('load', async (event) => {
  const usres = await fetch(`https://cdn.jsdelivr.net/npm/us-atlas@3/states-albers-10m.json`)
  window.us = await usres.json()
  map(window.data, window.us)
});

const STATES = {
  'AL': 'Alabama',
  'AK': 'Alaska',
  'AS': 'American Samoa',
  'AZ': 'Arizona',
  'AR': 'Arkansas',
  'CA': 'California',
  'CO': 'Colorado',
  'CT': 'Connecticut',
  'DE': 'Delaware',
  'DC': 'District Of Columbia',
  'FM': 'Federated States Of Micronesia',
  'FL': 'Florida',
  'GA': 'Georgia',
  'GU': 'Guam',
  'HI': 'Hawaii',
  'ID': 'Idaho',
  'IL': 'Illinois',
  'IN': 'Indiana',
  'IA': 'Iowa',
  'KS': 'Kansas',
  'KY': 'Kentucky',
  'LA': 'Louisiana',
  'ME': 'Maine',
  'MH': 'Marshall Islands',
  'MD': 'Maryland',
  'MA': 'Massachusetts',
  'MI': 'Michigan',
  'MN': 'Minnesota',
  'MS': 'Mississippi',
  'MO': 'Missouri',
  'MT': 'Montana',
  'NE': 'Nebraska',
  'NV': 'Nevada',
  'NH': 'New Hampshire',
  'NJ': 'New Jersey',
  'NM': 'New Mexico',
  'NY': 'New York',
  'NC': 'North Carolina',
  'ND': 'North Dakota',
  'MP': 'Northern Mariana Islands',
  'OH': 'Ohio',
  'OK': 'Oklahoma',
  'OR': 'Oregon',
  'PW': 'Palau',
  'PA': 'Pennsylvania',
  'PR': 'Puerto Rico',
  'RI': 'Rhode Island',
  'SC': 'South Carolina',
  'SD': 'South Dakota',
  'TN': 'Tennessee',
  'TX': 'Texas',
  'UT': 'Utah',
  'VT': 'Vermont',
  'VI': 'Virgin Islands',
  'VA': 'Virginia',
  'WA': 'Washington',
  'WV': 'West Virginia',
  'WI': 'Wisconsin',
  'WY': 'Wyoming',
}
