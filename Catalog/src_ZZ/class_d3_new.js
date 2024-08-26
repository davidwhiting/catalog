const screenWidth = 800;
const boxWidth = 110;
const boxHeight = 40;
const textOffsetX = 10; 
const textOffsetY = 25;
const sessionOffset = 60;
const headerRow = 20;

const yGap = 4;
const boxSpace = boxHeight + yGap;

// ---------------------------------------------
// Define x coordinates for rectangles
// if sessions, then 2.25*boxWidth else boxWidth

//const bin = [10];
//for (let k=0; k <=30; k++) {
//    bin.push(bin[k] + 20 + 2.25*boxWidth);
//}

const bin = Array.from({length: 32}, (_, k) => k === 0 ? 10 : bin[k-1] + 20 + 2.25*boxWidth);
// ---------------------------------------------

// ---------------------------------------------
// Define y coordinates for rectangles

//const row = [80];
//for (let k=0; k <=10; k++) {
//    row.push(row[k] + boxSpace);
//}

const row = Array.from({length: 12}, (_, k) => 80 + k * boxSpace);
// ---------------------------------------------

const semesterData = Array.from({length: 17 * 4}, (_, i) => {
  const year = Math.floor(i / 4) + 2024;
  const season = ['WINTER', 'SPRING', 'SUMMER', 'FALL'][i % 4];
  return `${season} ${year}`;
});

function render(data) {
  // Start Nested Functions
  const drawColumn = (period, data) => {
    const filteredData = data.filter(item => item.period === period);
    let anyItem = false;
    for (let j = 0; j < data.length; j++) {
      const offset = (j % 3 - 1) * sessionOffset;
      const item = filteredData[j];
      if (item) {
        anyItem = true;
        const fullname = `${item.name} (${item.credits})`;
        drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
      }
    }
    if (anyItem) {
      drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
    }
  };

  const drawRectangle = (x, y, name, color, textcolor, description='') => {
    const g = zoomable.append("g");
    g.append("rect")
      .attr("x", x)
      .attr("y", y)
      .attr("width", boxWidth)
      .attr("height", boxHeight)
      .style("fill", color)
      .classed("movable", true);
    g.append("text")
      .attr("x", x + textOffsetX)
      .attr("y", y + textOffsetY)
      .text(name)
      .attr("fill", textcolor)
      .style("font-size", "12px")
      .style("font-family", "Arial")
      .style("font-weight", "bold")
      .classed("movable", true);
    g.append("description")
      .text(description);
  };

  const drawHeader = (x, y, name, color, textcolor, description='') => {
    const g = zoomable.append("g");
    g.append("rect")
      .attr("x", x - sessionOffset)
      .attr("y", y)
      .attr("width", boxWidth + 2 * sessionOffset)
      .attr("height", boxHeight)
      .style("fill", color)
      .classed("movable", true);
    g.append("text")
      .attr("x", x - sessionOffset + 2*textOffsetX)
      .attr("y", y + textOffsetY)
      .text(name)
      .attr("fill", textcolor)
      .style("font-size", "14px")
      .style("font-family", "Arial")
      .style("font-weight", "bold")
      .classed("movable", true);
    g.append("description")
      .text(description);
  };
  // End of Nested Functions

  zoomable.selectAll(".movable").remove();
  const maxPeriod = d3.max(data, d => d.period);
  for (let j = 0; j <= maxPeriod; j++) {
    drawColumn(j, data);
  }
}

// Select the body and create SVG
const svg = d3.select("body")
  .append('svg')
    .attr('id', 'datavizArea')
    .attr('height', 300)
    .attr('width', 900);

const zoomable = svg.append("g");

const zoom = d3.zoom()
  .on("zoom", () => {
    zoomable.attr("transform", d3.event.transform);
  });

svg.call(zoom)
  .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));

// Error handling example
function safeRender(data) {
  try {
    if (!Array.isArray(data)) {
      throw new Error('Input data must be an array');
    }
    render(data);
  } catch (error) {
    console.error('Error rendering chart:', error);
    // You could also display an error message to the user here
  }
}