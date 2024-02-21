from h2o_wave import main, app, Q, site, ui, on, run_on, data, graphics as g
from typing import Optional, List
import pandas as pd
import json
import os.path

# The example D3 Javascript file is located in the same directory as this example; get its path
d3_js_script_filename = os.path.join(os.path.dirname(__file__), 'plot_d3.js')
#data_json_filename = os.path.join(os.path.dirname(__file__), 'data.json')

# Upload the script to the server. Typically, you'd do this only once, when your app is installed.
# move this to the init section?
d3_js_script_path, = site.upload([d3_js_script_filename])
#data_json_path, = site.upload([data_json_filename])

#rawdata = pd.read_json(data_json_path)

data_json = [
    {
        "seq": 1,
        "name": "PACE 111B",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1
    },
    {
        "seq": 2,
        "name": "LIBS 150",
        "credits": 1,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1
    },
    {
        "seq": 3,
        "name": "WRTG 111",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1
    },
    {
        "seq": 4,
        "name": "WRTG 112",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 5,
        "name": "NUTR 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 6,
        "name": "BMGT 110",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 2
    },
    {
        "seq": 7,
        "name": "SPCH 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 8,
        "name": "STAT 200",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 9,
        "name": "IFSM 300",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 3
    },
    {
        "seq": 10,
        "name": "ACCT 220",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 11,
        "name": "HUMN 100",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 12,
        "name": "BIOL 103",
        "credits": 4,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 5
    },
    {
        "seq": 13,
        "name": "ECON 201",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 4
    },
    {
        "seq": 14,
        "name": "ARTH 334",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 5
    },
    {
        "seq": 15,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 6
    },
    {
        "seq": 16,
        "name": "ECON 203",
        "credits": 3,
        "color": "red",
        "textcolor": "white",
        "prerequisite": "",
        "period": 6
    },
    {
        "seq": 17,
        "name": "ACCT 221",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "ACCT 220",
        "period": 6
    },
    {
        "seq": 18,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 19,
        "name": "BMGT 364",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 20,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 7
    },
    {
        "seq": 21,
        "name": "BMGT 365",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "BMGT 364",
        "period": 8
    },
    {
        "seq": 22,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 8
    },
    {
        "seq": 23,
        "name": "MRKT 310",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 8
    },
    {
        "seq": 24,
        "name": "WRTG 394",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "WRTG 112",
        "period": 9
    },
    {
        "seq": 25,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 9
    },
    {
        "seq": 26,
        "name": "BMGT 380",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 9
    },
    {
        "seq": 27,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 28,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 29,
        "name": "HRMN 300",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 10
    },
    {
        "seq": 30,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 11
    },
    {
        "seq": 31,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 11
    },
    {
        "seq": 32,
        "name": "FINC 330",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "ACCT 221 & STAT 200",
        "period": 11
    },
    {
        "seq": 33,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 34,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 35,
        "name": "BMGT 496",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "",
        "period": 12
    },
    {
        "seq": 36,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 37,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 38,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 13
    },
    {
        "seq": 39,
        "name": "ELECTIVE",
        "credits": 3,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "",
        "period": 14
    },
    {
        "seq": 40,
        "name": "BMGT 495",
        "credits": 3,
        "color": "blue",
        "textcolor": "white",
        "prerequisite": "BMGT 365 & MRKT 310 & FINC 330",
        "period": 14
    },
    {
        "seq": 41,
        "name": "CAPSTONE",
        "credits": 1,
        "color": "yellow",
        "textcolor": "black",
        "prerequisite": "FINC 330",
        "period": 14
    }
]


html_template_example = '''
<!DOCTYPE html>
<html>
<head>
  <script src="https://d3js.org/d3.v5.js"></script>
</head>
<body style="margin:0; padding:0">
  <script src="{script_path}"></script>
  <script>render({data})</script>
</body>
</html>
'''

html_code = '''
<!DOCTYPE html>
<html>
<head>

  <style>
    body {
      text-align: center;
    }
    
    svg {
      margin-top: 12px;
      border: 1px solid #aaa;
    }
  </style>

  <!-- Load d3.js -->
  <script src='https://d3js.org/d3.v5.js'></script>
</head>

<body>

  <script type="module">
      const data = [
        {
            seq: 1,
            name: "PACE 111B",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 1
        },
        {
            seq: 2,
            name: "LIBS 150",
            credits: 1,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 1
        },
        {
            seq: 3,
            name: "WRTG 111",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 1
        },
        {
            seq: 4,
            name: "WRTG 112",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 2
        },
        {
            seq: 5,
            name: "NUTR 100",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 2
        },
        {
            seq: 6,
            name: "BMGT 110",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 2
        },
        {
            seq: 7,
            name: "SPCH 100",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 3
        },
        {
            seq: 8,
            name: "STAT 200",
            credits: 3,
            color: "red",
            textcolor: "white",
            prerequisite: "",
            period: 3
        },
        {
            seq: 9,
            name: "IFSM 300",
            credits: 3,
            color: "red",
            textcolor: "white",
            prerequisite: "",
            period: 3
        },
        {
            seq: 10,
            name: "ACCT 220",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 4
        },
        {
            seq: 11,
            name: "HUMN 100",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 4
        },
        {
            seq: 12,
            name: "BIOL 103",
            credits: 4,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 5
        },
        {
            seq: 13,
            name: "ECON 201",
            credits: 3,
            color: "red",
            textcolor: "white",
            prerequisite: "",
            period: 4
        },
        {
            seq: 14,
            name: "ARTH 334",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "",
            period: 5
        },
        {
            seq: 15,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 6
        },
        {
            seq: 16,
            name: "ECON 203",
            credits: 3,
            color: "red",
            textcolor: "white",
            prerequisite: "",
            period: 6
        },
        {
            seq: 17,
            name: "ACCT 221",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "ACCT 220",
            period: 6
        },
        {
            seq: 18,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 7
        },
        {
            seq: 19,
            name: "BMGT 364",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 7
        },
        {
            seq: 20,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 7
        },
        {
            seq: 21,
            name: "BMGT 365",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "BMGT 364",
            period: 8
        },
        {
            seq: 22,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 8
        },
        {
            seq: 23,
            name: "MRKT 310",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 8
        },
        {
            seq: 24,
            name: "WRTG 394",
            credits: 3,
            color: "green",
            textcolor: "white",
            prerequisite: "WRTG 112",
            period: 9
        },
        {
            seq: 25,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 9
        },
        {
            seq: 26,
            name: "BMGT 380",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 9
        },
        {
            seq: 27,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 10
        },
        {
            seq: 28,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 10
        },
        {
            seq: 29,
            name: "HRMN 300",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 10
        },
        {
            seq: 30,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 11
        },
        {
            seq: 31,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 11
        },
        {
            seq: 32,
            name: "FINC 330",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "ACCT 221 & STAT 200",
            period: 11
        },
        {
            seq: 33,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 12
        },
        {
            seq: 34,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 12
        },
        {
            seq: 35,
            name: "BMGT 496",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "",
            period: 12
        },
        {
            seq: 36,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 13
        },
        {
            seq: 37,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 13
        },
        {
            seq: 38,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 13
        },
        {
            seq: 39,
            name: "ELECTIVE",
            credits: 3,
            color: "yellow",
            textcolor: "black",
            prerequisite: "",
            period: 14
        },
        {
            seq: 40,
            name: "BMGT 495",
            credits: 3,
            color: "blue",
            textcolor: "white",
            prerequisite: "BMGT 365 & MRKT 310 & FINC 330",
            period: 14
        },
        {
            seq: 41,
            name: "CAPSTONE",
            credits: 1,
            color: "yellow",
            textcolor: "black",
            prerequisite: "FINC 330",
            period: 14
        }
      ];
    var transferCredits = false;    

    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 1.75*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {
        bin.push(bin[k] + 20 + 2.25*boxWidth);
    }
    
    // Define y coordinates for rectangles
    const yGap = 4;
    const boxSpace = boxHeight + yGap;
    var row = [80];
    for (let k=0; k <=10; k++) {
        row.push(row[k] + boxSpace);
    }

    var semesterData = [];
    const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
    for (let year = 2024; year <= 2040; year++) {
      for (let season of seasons) {
        semesterData.push(`${season} ${year}`);
      }
    }
    
    function render(data) {
      // Start Nested Functions
      function drawColumn(period, data) {
        var filteredData = data.filter(item => item.period === period);
        var anyItem = false;
        for (let j = 0; j < data.length; j++) {
          let offset = (j % 3 - 1) * sessionOffset;
          let item = filteredData[j];
          if (item !== undefined) {
            anyItem = true;
            let fullname = `${item.name} (${item.credits})`;
            drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
          }
        }
        if (anyItem) {
          drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
        }
      }
      function drawRectangle(x, y, name, color, textcolor, description='') {
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
      // End of Nested Functions
      zoomable.selectAll(".movable").remove();
      var maxPeriod = Math.max(...data.map(item => item.period));
      for (let j = 0; j <= maxPeriod; j++) {
        drawColumn(j, data);
      }
    }

    // Select the body
    var body = d3.select("body");

    // Zoom behavior
    var svg = body.append('svg')
      .attr('id', 'datavizArea')
      .attr('height', 300)
      .attr('width', 900);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
      .on("zoom", function() {
        zoomable.attr("transform", d3.event.transform);
      });
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));

    render(data);
  
  </script>

</body>
</html>
'''

javascript_code = '''
const screenWidth = 800;
const boxWidth = 110;
const boxHeight = 40;
const textOffsetX = 10; 
const textOffsetY = 25;
const sessionOffset = 35;
const headerRow = 20;

// Define x coordinates for rectangles
var bin = [10];
// if sessions, then 1.75*boxWidth else boxWidth
for (let k=0; k <=30; k++) {
    bin.push(bin[k] + 20 + 1.75*boxWidth);
}
    
// Define y coordinates for rectangles
const yGap = 4;
const boxSpace = boxHeight + yGap;
var row = [80];
for (let k=0; k <=10; k++) {
    row.push(row[k] + boxSpace);
}

var semesterData = [];
const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
for (let year = 2024; year <= 2040; year++) {
  for (let season of seasons) {
    semesterData.push(`${season} ${year}`);
  }
}
    
function render(data) {
  // Start Nested Functions
  function drawColumn(period, data) {
    var filteredData = data.filter(item => item.period === period);
    var anyItem = false;
    for (let j = 0; j < data.length; j++) {
      let offset = (j % 3 - 1) * sessionOffset;
      let item = filteredData[j];
      if (item !== undefined) {
        anyItem = true;
        let fullname = `${item.name} (${item.credits})`;
        drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
      }
    }
    if (anyItem) {
      drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
    }
  }
  function drawRectangle(x, y, name, color, textcolor, description='') {
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
  // End of Nested Functions
  zoomable.selectAll(".movable").remove();
  var maxPeriod = Math.max(...data.map(item => item.period));
  for (let j = 0; j <= maxPeriod; j++) {
    drawColumn(j, data);
  }
}

// Select the body
var body = d3.select("body");

// Zoom behavior
var svg = body.append('svg')
  .attr('id', 'datavizArea')
  .attr('height', 400)
  .attr('width', 800);
var zoomable = svg.append("g");
var zoom = d3.zoom()
  .on("zoom", function() {
    zoomable.attr("transform", d3.event.transform);
  });
svg.call(zoom);

render(data);

//// Load the data from a JSON file
//d3.json('data.json').then(function(data) {
//  // Use the loaded data
//  render(data);
//}).catch(function(error) {
//  console.log('Error loading data: ' + error);
//});
'''

# This data is hard-coded here for simplicity.
# During production use, this data would be the output of some compute routine.
example_data = [
    [11975, 5871, 8916, 2868],
    [1951, 10048, 2060, 6171],
    [8010, 16145, 8090, 8045],
    [1013, 990, 940, 6907],
]

# Calculate these in the future from student selections
completion_date = 'Spring 2027'
terms_remaining = 14
total_credits_remaining = 120
cost_per_credit_bs = [324, 499]
# display instate or out-of-state status

in_state_tuition = True
if in_state_tuition:
    cost_per_credit = cost_per_credit_bs[0]
else:
    cost_per_credit = cost_per_credit_bs[1]

credits_next_term = 7
total_cost_remaining = "${:,}".format(total_credits_remaining * cost_per_credit)
next_term_cost = "${:,}".format(credits_next_term * cost_per_credit)
#total_cost_str = "${:,.2f}".format(total_cost_remaining)
#total_cost_str = "${:,}".format(total_cost_remaining)

# Plug JSON-serialized data into our html template
example_html = html_template_example.format(script_path=d3_js_script_path, data=json.dumps(example_data))

def get_form_items(value: Optional[float]):
    return [
        ui.text(f'spinbox_trigger={value}'),
        ui.spinbox(name='spinbox_trigger', label='Credits', trigger=True),
    ]

sample_markdown = '''
## Notes and To Do's:

To Do:

- Find icons and change them.
- Add dropdown or tab menus for personalization
- Add menus for elective exploration and selection
- Add menus for minor exploration and selection
- Add checkbox or toggle switch for adding completed credits

Table:

| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Item 1   | Item 2   | Item 3   |
| Item 1   | Item 2   | Item 3   |
| Item 1   | Item 2   | Item 3   |
'''

@app('/')
async def serve(q: Q):
    # First time a browser comes to the app
    if not q.client.initialized:
        await init(q)
        q.client.initialized = True

    if q.args.show_inputs:
        q.page['sessions'].items = [
            ui.text(f'selected={q.args.checklist}'),
#            ui.button(name='show_form', label='Back', primary=True),
        ]
    else:
        q.page['example'] = ui.form_card(box='rightgrid', items=[
            ui.checklist(name='checklist', label='Sessions Attending',
                         choices=[ui.choice(name=x, label=x) for x in ['Session 1', 'Session 2', 'Session 3']]),
#            ui.button(name='show_inputs', label='Submit', primary=True),
        ])

#    # spinbox w/ trigger
#    if not q.client.initialized:
#        q.page['spinbox'] = ui.form_card(box='slider', items=get_form_items(None))
#        q.client.initialized = True
#    if q.args.spinbox_trigger is not None:
#        q.page['spinbox'].items = get_form_items(q.args.spinbox_trigger)

    if q.args.show_inputs:
        q.page['spinbox'].items = [
            ui.text(f'spinbox={q.args.spinbox}'),
#            ui.button(name='show_form', label='Back', primary=True),
        ]
    else:
        q.page['spinbox'] = ui.form_card(box='rightgrid', items=[
            ui.spinbox(name='spinbox', label='Courses per Session', min=1, max=3, step=1, value=1),
#            ui.button(name='show_inputs', label='Submit', primary=True),
        ])

#    # spinbox w/ trigger
#    if not q.client.initialized:
#        q.page['spinbox'] = ui.form_card(box='slider', items=get_form_items(None))
#        q.client.initialized = True
#    if q.args.spinbox_trigger is not None:
#        q.page['spinbox'].items = get_form_items(q.args.spinbox_trigger)

    # slider
    if q.args.show_inputs:
        q.page['slider'].items = [
            ui.text(f'slider={q.args.slider}'),
#            ui.button(name='show_form', label='Back', primary=True),
        ]
    else:
        q.page['slider'] = ui.form_card(box='rightgrid', items=[
            ui.slider(name='slider', label='Max Credits per Term', min=1, max=15, step=1, value=9),
#            ui.button(name='show_inputs', label='Submit', primary=True),
        ])

    # Other browser interactions
    await run_on(q)
    await q.page.save()


async def init(q: Q) -> None:
    q.client.cards = set()
    q.client.dark_mode = False

    q.page['meta'] = ui.meta_card(
        box='',
        title='UMGC Wave App',
        theme='ember',
        layouts=[
            ui.layout(
                breakpoint='xs',
                min_height='100vh',
#                max_width='1200px',
                max_width='100vw',
                zones=[
                    ui.zone('header'),
                    ui.zone('content', size='1', zones=[
                        ui.zone('horizontal', direction=ui.ZoneDirection.COLUMN, justify='center'),
                        ui.zone('horizontal2', direction=ui.ZoneDirection.ROW, size='1', 
                            zones=[
                               ui.zone('left1',  size='25%', direction=ui.ZoneDirection.COLUMN),
                               ui.zone('left2',  size='25%', direction=ui.ZoneDirection.COLUMN),
                               ui.zone('right1', size='49%', direction=ui.ZoneDirection.COLUMN),
                               ui.zone('right2', size= '1%', direction=ui.ZoneDirection.COLUMN),
                        ]),
                        ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center', 
                            zones=[
                            #   ui.zone('leftgrid', size='5%'),
                               ui.zone('midgrid', size='80%'),
                               ui.zone('rightgrid', size='20%', direction=ui.ZoneDirection.COLUMN),
                        ]),
                        ui.zone('slider', direction=ui.ZoneDirection.ROW, justify='center'),
                        ui.zone('notes', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center', 
                            zones=[
                               ui.zone('leftnote',  size='70%'),
                               ui.zone('rightnote', size='30%'),
                        ]),
                        
                    ]),
                    ui.zone(name='footer'),
                ]
            )
        ]
    )

    image_path, = await q.site.upload(['umgc-logo.png'])
    q.page['header'] = ui.header_card(
        box='header',
        title='UMGC Curriculum Assistant',
        subtitle="Title TBD",
        image=image_path,
#        items=[ui.menu(icon='', items=[ui.command(name='change_theme', icon='ClearNight', label='Dark Mode')])]
        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)]
    )
    
    menu_width = '250px'
    # To do: Load menus from json

    q.page['dropdown_menus'] = ui.form_card(
        box='horizontal',
        items=[
            ui.inline(
                items=[
                    ui.dropdown(
                        name='degree', 
                        label='Degree', 
                        value=q.args.degree,
                        trigger=True,
                        width=menu_width,
                        choices=[
                            ui.choice(name='AS', label="Associate"),
                            ui.choice(name='BS', label="Bachelor's"),
                            ui.choice(name='MS', label="Master's"),
                            ui.choice(name='DC', label="Doctorate"),
                            ui.choice(name='UC', label="Undergraduate Certificate"),
                            ui.choice(name='GC', label="Graduate Certificate")
                    ]),
                    ui.dropdown(
                        name='area_of_study', 
                        label='Area of Study', 
                        value=q.args.area_of_study,
                        trigger=False,
                        disabled=False,
                        width=menu_width,
                        choices=[
                            ui.choice(name='BM', label='Business & Management'),
                            ui.choice(name='CS', label='Cybersecurity'),
                            ui.choice(name='DA', label='Data Analytics'),
                            ui.choice(name='ET', label='Education & Teaching'),
                            ui.choice(name='HS', label='Healthcare & Science'),
                            ui.choice(name='LA', label='Liberal Arts & Communications'),
                            ui.choice(name='PS', label='Public Safety'),
                            ui.choice(name='IT', label='IT & Computer Science')
                    ]),
                    ui.dropdown(
                        name='major', 
                        label='Major', 
                        value=q.args.major,
                        trigger=False,
                        disabled=False,
                        width=menu_width,
                        choices=[
                            ui.choice(name='AC', label='Accounting'),
                            ui.choice(name='BA', label='Business Administration'),
                            ui.choice(name='FI', label='Finance'),
                            ui.choice(name='HR', label='Human Resource Management'),
                            ui.choice(name='MS', label='Management Studies'),
                            ui.choice(name='MK', label='Marketing'),
                    ]),
                ]
            )
        ]
    )

#    q.page['textbox'] = ui.form_card(
#        box='left1',
#        items=[ui.textbox(name='textbox_default', label='Student Name', 
#                          value='John Doe', disabled=True)]
#    )

    q.page['toggle'] = ui.form_card(box='rightgrid', items=[
        ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
    ])

    q.page['footer'] = ui.footer_card(
        box='footer',
        caption='Made using [H2O Wave](https://wave.h2o.ai).'
    )

#    q.page['d3plot_example'] = ui.frame_card(
#        box=ui.box('midgrid', height='600px', width='600px'),
#        title='D3 Plot',
#        content=example_html,
#    )

    q.page['d3plot'] = ui.frame_card(
        box=ui.box('midgrid', height='600px', width='1000px'),
        title='Tentative Course Schedule',
        content=html_code,
    )

#    q.page['graduation_year'] = ui.tall_gauge_stat_card(
#        box=ui.box('left1', height='150px',),
#        title='Completed Credits',
#        value='={{intl foo minimum_fraction_digits=0 maximum_fraction_digits=0}}',
#        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
#        plot_color='$blue',
#        progress=0.56,
#        data=dict(foo=60, bar=0.56),
#    )

#    q.page['graduation_year2'] = ui.wide_gauge_stat_card(
#        box=ui.box('right1', height='100px',),
#        title='Finish Date',
#        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
#        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
#        plot_color='$red',
#        progress=0.56,
#        data=dict(foo=123, bar=0.56),
#    )

#    q.page['graduation_year4'] = ui.wide_bar_stat_card(
#        box=ui.box('left1', 
##                   height='100px',),
#                   size='1',),
#        title='Finish Date',
#        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
#        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
#        plot_color='$green',
#        progress=0.56,
#        data=dict(foo=123, bar=0.56),
#    )

    q.page['stats'] = ui.form_card(box='horizontal', items=[
        ui.stats(justify='between', items=[
            ui.stat(label='Credits', value=str(total_credits_remaining), caption='Credits Remaining', icon='Education'),            
            ui.stat(label='Tuition', value=next_term_cost, caption='Estimated Tuition', icon='Money'),
            ui.stat(label='Terms Remaining', value=str(terms_remaining), caption='Terms Remaining', icon='Education'),
            ui.stat(label='Finish Date', value=completion_date, caption='(Estimated)', icon='SpecialEvent'),
            ui.stat(label='Total Tuition', value=total_cost_remaining, caption='Estimated Tuition', icon='Money'),
        ])
    ])

#    q.page['tall_stats'] = ui.tall_stats_card(
##        box=ui.box('right2', height='200px',),
#        box=ui.box('left2'),
#        items=[
#            ui.stat(label='FINISH DATE', value=completion_date),
#            ui.stat(label='TERMS REMAINING', value=str(terms_remaining)),
#            ui.stat(label='CREDITS LEFT', value=str(total_credits_remaining)), 
#        ]
#    )

    q.page['markdown'] = ui.form_card(
        box='rightnote',
        items=[ui.text(sample_markdown)]
    )

### Potential alternate way to recreate D3 graphic of coursework
#
#    q.page['stages'] = ui.graphics_card(
#        box='leftnote', view_box='0 0 100 100', width='100%', height='100%',
#        stage=g.stage(
##            face=g.circle(cx='50', cy='50', r='45', fill='#111', stroke_width='2px', stroke='#f55'),
#            face=g.rect(x='-75', y='0', width='250', height='100', 
#                        fill='white', stroke_width='1px', stroke='black'),
#        ),
#        scene=g.scene(
#            hour=g.rect(x='0', y='5', width='15', height='5', fill='red', stroke='black'),
#            min=g.text('(0,0)', x='10', y='10' , fontsize='6px')
##            min=g.rect(x='48.5', y='12.5', width='3', height='40', rx='2', fill='#333', stroke='#555'),
##            sec=g.line(x1='50', y1='50', x2='50', y2='16', stroke='#f55', stroke_width='1px'),
#        ),
#    )

@on()
async def home(q: Q):
    clear_cards(q)
    add_card(q, 'form', ui.form_card(box='vertical', items=[ui.text('This is my app!')]))


@on()
async def change_theme(q: Q):
    """Change the app from light to dark mode"""
    if q.client.dark_mode:
        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='ClearNight', label='Dark mode')])]
        q.page["meta"].theme = "ember"
        q.client.dark_mode = False
    else:
        q.page["header"].items = [ui.menu([ui.command(name='change_theme', icon='Sunny', label='Light mode')])]
        q.page["meta"].theme = "ember"
        q.client.dark_mode = True


# Use for cards that should be deleted on calling `clear_cards`. Useful for routing and page updates.
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card

def clear_cards(q, ignore=[]) -> None:
    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
