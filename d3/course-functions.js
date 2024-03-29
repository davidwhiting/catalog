// Your D3 script here
//import { data } from "./data.js";
//console.log(data);

let originalData = [  
  { seq:  1, name: 'PACE 111B', credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  2, name: 'LIBS 150',  credits: 1, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  3, name: 'WRTG 111',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  4, name: 'WRTG 112',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  5, name: 'NUTR 100',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  6, name: 'BMGT 110',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq:  7, name: 'SPCH 100',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  8, name: 'STAT 200',  credits: 3, color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq:  9, name: 'IFSM 300',  credits: 3, color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq: 10, name: 'ACCT 220',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 11, name: 'HUMN 100',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq: 12, name: 'BIOL 103',  credits: 4, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq: 13, name: 'ECON 201',  credits: 3, color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq: 14, name: 'ARTH 334',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq: 15, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 16, name: 'ECON 203',  credits: 3, color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq: 17, name: 'ACCT 221',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: 'ACCT 220' },  
  { seq: 18, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 19, name: 'BMGT 364',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 20, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 21, name: 'BMGT 365',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: 'BMGT 364' },
  { seq: 22, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 23, name: 'MRKT 310',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 24, name: 'WRTG 394',  credits: 3, color: 'green',  textcolor: 'white', prerequisite: 'WRTG 112' },
  { seq: 25, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 26, name: 'BMGT 380',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 27, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 28, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 29, name: 'HRMN 300',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 30, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 31, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 32, name: 'FINC 330',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: 'ACCT 221 & STAT 200' },  
  { seq: 33, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 34, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 35, name: 'BMGT 496',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 36, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 37, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 38, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 39, name: 'ELECTIVE',  credits: 3, color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 40, name: 'BMGT 495',  credits: 3, color: 'blue',   textcolor: 'white', prerequisite: 'BMGT 365 & MRKT 310 & FINC 330' },
  { seq: 41, name: 'CAPSTONE',  credits: 1, color: 'yellow', textcolor: 'black', prerequisite: 'FINC 330' }
];

let transferData = [  
  { seq:  1, name: 'PACE 111B', credits: 3, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  2, name: 'LIBS 150',  credits: 1, complete: 'true',  color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  3, name: 'WRTG 111',  credits: 3, complete: 'true',  color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  4, name: 'WRTG 112',  credits: 3, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  5, name: 'NUTR 100',  credits: 3, complete: 'trans', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  6, name: 'BMGT 110',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq:  7, name: 'SPCH 100',  credits: 3, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq:  8, name: 'STAT 200',  credits: 3, complete: 'true',  color: 'black',  textcolor: 'white', prerequisite: '' },
  { seq:  9, name: 'IFSM 300',  credits: 3, complete: 'false', color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq: 10, name: 'ACCT 220',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 11, name: 'HUMN 100',  credits: 3, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq: 12, name: 'BIOL 103',  credits: 4, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq: 13, name: 'ECON 201',  credits: 3, complete: 'false', color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq: 14, name: 'ARTH 334',  credits: 3, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: '' },
  { seq: 15, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 16, name: 'ECON 203',  credits: 3, complete: 'false', color: 'red',    textcolor: 'white', prerequisite: '' },
  { seq: 17, name: 'ACCT 221',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: 'ACCT 220' },  
  { seq: 18, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 19, name: 'BMGT 364',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 20, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 21, name: 'BMGT 365',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: 'BMGT 364' },
  { seq: 22, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 23, name: 'MRKT 310',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 24, name: 'WRTG 394',  credits: 3, complete: 'false', color: 'green',  textcolor: 'white', prerequisite: 'WRTG 112' },
  { seq: 25, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 26, name: 'BMGT 380',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 27, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 28, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 29, name: 'HRMN 300',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 30, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 31, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 32, name: 'FINC 330',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: 'ACCT 221 & STAT 200' },  
  { seq: 33, name: 'ELECTIVE',  credits: 3, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 34, name: 'TRANSFER',  credits: 3, complete: 'trans', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 35, name: 'BMGT 496',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: '' },
  { seq: 36, name: 'ELECTIVE',  credits: 3, complete: 'trans', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 37, name: 'ELECTIVE',  credits: 3, complete: 'trans', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 38, name: 'ELECTIVE',  credits: 3, complete: 'trans', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 39, name: 'ELECTIVE',  credits: 3, complete: 'trans', color: 'yellow', textcolor: 'black', prerequisite: '' },
  { seq: 40, name: 'BMGT 495',  credits: 3, complete: 'false', color: 'blue',   textcolor: 'white', prerequisite: 'BMGT 365 & MRKT 310 & FINC 330' },
  { seq: 41, name: 'CAPSTONE',  credits: 1, complete: 'false', color: 'yellow', textcolor: 'black', prerequisite: 'FINC 330 & BMGT 496' }
];

let data = originalData;
//    let data = transferData;

var transferCredits = false;

// Legend color stuff

var screenWidth = 800;
var boxWidth = 110;
var boxHeight = 40;
var textOffsetX = 10; 
var textOffsetY = 25;
var sessionOffset = 35;

function drawRectangleNew(x, y, name, color, textcolor, description='') {
  var g = zoomable.append("g");
  
  g.append("rect")
    .attr("x", x)
    .attr("y", y)
    .attr("width", boxWidth)
    .attr("height", boxHeight)
    .style("fill", color)
    .classed("movable", true); // Add the "movable" class
  
  g.append("text")
    .attr("x", x + textOffsetX)
    .attr("y", y + textOffsetY)
    .text(name)
    .attr("fill", textcolor)
    .style("font-size", "12px")
    .style("font-family", "Arial")
    .style("font-weight", "bold")
    .classed("movable", true); // Add the "movable" class

  // Add a tooltip
  g.append("description")
    .text(description);
}

function drawHeader(x, y, name, color, textcolor, description='') {
  var g = zoomable.append("g");
  
  g.append("rect")
    .attr("x", x - sessionOffset)
    .attr("y", y)
    .attr("width", boxWidth + 2 * sessionOffset)
    .attr("height", boxHeight)
    .style("fill", color)
    .classed("movable", true); // Add the "movable" class
  
  g.append("text")
    .attr("x", x - sessionOffset + 2*textOffsetX)
    .attr("y", y + textOffsetY)
    .text(name)
    .attr("fill", textcolor)
    .style("font-size", "14px")
    .style("font-family", "Arial")
    .style("font-weight", "bold")
    .classed("movable", true); // Add the "movable" class

  // Add a tooltip
  g.append("description")
    .text(description);
}

let semesterData = [];
const seasons = ['SPRING', 'SUMMER', 'FALL'];
for (let year = 2024; year <= 2040; year++) {
  for (let season of seasons) {
    semesterData.push(`${season} ${year}`);
  }
}

function drawColumn(period, data, transfer=false) {
  let filteredData = data.filter(item => item.period === period);
  let anyItem = false;
//      let totalCredits = 0;
  for (let j = 0; j < data.length; j++) {
    let offset = (j % 3 - 1) * sessionOffset;
    let item = filteredData[j];
    if (item !== undefined) {
      anyItem = true;
//          let totalCredits = totalCredits + item.credits; 
      let fullname = `${item.name} (${item.credits})`;
//          let fullname = `${summary.totalCredits[period+1]} (${summary.courseCount[period+1]}`;
      drawRectangleNew(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
    }
  }
  if (anyItem) {
    drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
  }
}

function drawSchedule(data) {
  // find max 
  var maxPeriod = Math.max(...data.map(item => item.period));
  for (let j = 0; j <= maxPeriod; j++) {
    drawColumn(j, data);
  }
}

function drawTransferSchedule(data) {
  // find max 
  var maxPeriod = Math.max(...data.map(item => item.period));
  for (let j = 1; j <= maxPeriod; j++) {
    drawColumn(j, data, transfer=true);
  }
}

function assignBins(maxCredits, data) {
  // Initialize an array to keep track of the total credits in each bin
  let binCredits = [0];

  // Initialize an object to keep track of the bin of each course
  let courseBin = {};

  for (let j = 0; j < data.length; j++) {
    let item = data[j];

    // If the course is complete, assign it to bin 0 and continue to the next course
    if (item.complete === 'true') {
      courseBin[item.name] = 0;
      item.period = 0;
      item.color = 'black';
      item.textcolor = 'white';
    } else if (item.complete === 'trans') {
      courseBin[item.name] = 0;
      item.period = 0;
      item.color = 'gray';
      item.textcolor = 'black';  
    } else {

      // Assign bins with prerequisites
      let startBin = 1;
  
      // if prerequisite line non-empty
      if (item.prerequisite) {
        // Split the prerequisites string into an array of prerequisites
        let prerequisites = item.prerequisite.split(' & ');
  
        // Get the bin of each prerequisite
        let prerequisiteBins = prerequisites.map(prerequisite => courseBin[prerequisite]);
  
        // Find the maximum bin among the prerequisites
        let maxPrerequisiteBin = Math.max(...prerequisiteBins);
  
        // Assign the minimum bin
        startBin = maxPrerequisiteBin + 1; 
      }   
      let period = startBin;
  
      let done = 0;
      while (done === 0) {
        if (binCredits[period] === undefined) {
          binCredits[period] = item.credits;
          done = 1;
        } else if (binCredits[period] + item.credits > maxCredits) {
          period++;
        } else {
          binCredits[period] += item.credits;
          done = 1;
        }
      } 
      courseBin[item.name] = period;
      item.period = period;
    }
  }
}

function assignClasses(maxCredits, data) {
  // Initialize an array to keep track of the total credits in each bin
  let binCredits = [0];

  // Initialize an object to keep track of the bin of each course
  let courseBin = {};

  for (let j = 0; j < data.length; j++) {
    let item = data[j];

    // If the course is complete, assign it to bin 0 and continue to the next course
    if (item.complete === 'true') {
      courseBin[item.name] = 0;
      item.period = 0;
      item.color = 'black';
      item.textcolor = 'white';
    } else if (item.complete === 'trans') {
      courseBin[item.name] = 0;
      item.period = 0;
      item.color = 'gray';
      item.textcolor = 'black';  
    } else {

      // Assign bins with prerequisites
      let startBin = 1;
  
      // if prerequisite line non-empty
      if (item.prerequisite) {
        // Split the prerequisites string into an array of prerequisites
        let prerequisites = item.prerequisite.split(' & ');
  
        // Get the bin of each prerequisite
        let prerequisiteBins = prerequisites.map(prerequisite => courseBin[prerequisite]);
  
        // Find the maximum bin among the prerequisites
        let maxPrerequisiteBin = Math.max(...prerequisiteBins);
  
        // Assign the minimum bin
        startBin = maxPrerequisiteBin + 1; 
      }   
      let period = startBin;
  
      let done = 0;
      while (done === 0) {
        if (binCredits[period] === undefined) {
          binCredits[period] = item.credits;
          done = 1;
        } else if (binCredits[period] + item.credits > maxCredits) {
          period++;
        } else {
          binCredits[period] += item.credits;
          done = 1;
        }
      } 
      courseBin[item.name] = period;
      item.period = period;
    }
  }
}

function creditSummary(data) {
  // create sum of credits per period

  let summary = data.reduce((acc, item) => {
    // If the period doesn't exist in the accumulator, add it
    if (!acc[item.period]) {
      acc[item.period] = { totalCredits: 0, courseCount: 0 };
    }
  
    // Add the credits for the current item to the period
    acc[item.period].totalCredits += item.credits;
  
    // Increment the course count for the period
    acc[item.period].courseCount++;
  
    return acc;
  }, {});

  return summary;
}

// Define x coordinates for rectangles
var bin = [10];
// if sessions, then 1.5*boxWidth else boxWidth
for (let k=0; k <=30; k++) {
    bin.push(bin[k] + 20 + 1.75*boxWidth);
}

// Define y coordinates for rectangles
var yGap = 4;
var boxSpace = boxHeight + yGap;
var row = [80];
for (let k=0; k <=10; k++) {
    row.push(row[k] + boxSpace);
}

// define y coordinates for header rectangles
var headerRow = 20;

// quick hack for demo
// this is not the real way I want to do it!
function redraw(maxc, data, odata=originalData, tdata=transferData) {
  assignBins(maxc, odata);
  console.log(odata);
  assignBins(maxc, tdata);
  zoomable.selectAll(".movable").remove();
  if (transferCredits) {
//        drawTransferSchedule(tdata);
    drawSchedule(tdata);
  } else {
    drawSchedule(odata);
  }
}

function clearAll() {
   zoomable.selectAll(".movable").remove();
}

// end D3 script insertion

// Select the body
var body = d3.select("body");

// Append the SVG to the body after the dropdowns
var svg = body.append('svg')
  .attr('id', 'datavizArea')
  .attr('height', 400)
  .attr('width', 800);

// Define the zoomable group
var zoomable = svg.append("g");

// Define the zoom behavior
var zoom = d3.zoom()
  .on("zoom", function() {
    zoomable.attr("transform", d3.event.transform);
  });

// Apply the zoom behavior to your SVG
svg.call(zoom);
    
// set up default
redraw(9, data);

let summary = creditSummary(data);

body.append("h3")
.text("Transfer Credits:");

  // Append the checkbox to the body
  var checkboxDiv = body.append("div");
  
  var checkbox = checkboxDiv.append("input")
    .attr("type", "checkbox")
    .attr("id", "toggleHighlight")
    .attr("name", "toggleHighlight");
  
  checkboxDiv.append("label")
    .attr("for", "toggleHighlight")
    .text("Import Transfer Credits");
  
  // Add an event listener to the checkbox
  checkbox.on("change", function() {
    // Get the current state of the checkbox
    var isChecked = d3.select(this).property("checked");
  
    // If the checkbox is checked, run runPrerequisites(data, clicked=true)
    if (isChecked) {
      transferCredits = true;
      data = transferData;
      redraw(9, data);
    }
    // If the checkbox is not checked, set data to old
    else {
      transferCredits = false;
      data = originalData;
      redraw(9, data);
    }
  });
