import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g

project_data = [
    {
        "id": "1",
        "rank": "1",
        "category": "Catalog",
        "description": "Enter all undergraduate courses into DB",
        "status": "1.00",
        "tags": "Database",
        "group": "Database"
    },
    {
        "id": "2",
        "rank": "2",
        "category": "Catalog",
        "description": "Enter all graduate courses into DB",
        "status": "0.00",
        "tags": "Database"
    },
    {
        "id": "3",
        "rank": "3",
        "category": "Catalog",
        "description": "Enter all Associate's programs",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "4",
        "rank": "4",
        "category": "Catalog",
        "description": "Enter all Bachelor's Major programs",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "5",
        "rank": "5",
        "category": "Catalog",
        "description": "Enter all Bachelor's Minor programs",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "6",
        "rank": "6",
        "category": "Catalog",
        "description": "Enter all Undergraduate Certificates",
        "status": str(2 / 50),
        "tags": "Database"
    },
    {
        "id": "6",
        "rank": "6",
        "category": "Catalog",
        "description": "Enter all Master's programs",
        "status": str(2 / 50),
        "tags": "Database"
    },

    {
        "id": "3",
        "rank": "3",
        "category": "Wave",
        "description": "Make table menus active",
        "status": "0.00",
        "tags": "Wave"
    },
    {
        "id": "3",
        "rank": "3",
        "category": "Wave",
        "description": "Example Text",
        "status": "0.90",
        "tags": "Data,UI"
    },
    {
        "id": "5",
        "rank": "5",
        "category": "Example",
        "description": "Example Text",
        "status": "0.90",
        "tags": "Data,UI"
    },
    {
        "id": "4",
        "rank": "4",
        "category": "Example",
        "description": "Example Text",
        "status": "0.50",
        "tags": "Code"
    },
]

# used to be on app, not used now?
complete_records_query = '''
    SELECT 
        a.seq,
        a.name,
        a.program_id,
        a.class_id,
        a.course_type_id,
        b.title,
        b.description,
        b.prerequisites
    FROM 
        program_sequence a
    JOIN 
        courses b
    ON 
        a.class_id = b.id
    WHERE 
        a.program_id = ?
'''

# query moved to view
ge_query_j_old_delete_me = '''
    SELECT 
        b.id,
        b.name,
        b.title,
        b.credits,
        b.description,
        b.pre,
        b.pre_credits
    FROM 
        general_education a
    LEFT JOIN 
        courses b
    ON 
        a.course_id = b.id
    WHERE 
        b.general_education_requirements_id = ?
'''

ge_query_j = 'SELECT * FROM ge_view WHERE ge_id = ?'

complete_records_query = 'SELECT * FROM complete_records_view WHERE program_id = ?'

complete_student_records_query = 'SELECT * FROM student_records_view WHERE student_info_id = ?'


home_markdown = '''
# Notes

We need to allow for a view with exploration before someone logs in (suppose this is used by somebody not yet enrolled). We will add additional views for those that are logged in. E.g., completed courses, transfer credits, etc.

_**We assume someone is logged in at this point.**_

Once logged in, the home page will show important dashboard.


## Tab Steps Above (Currently Disabled)
### Login

### Import information

### Update Information

### Personalization

'''

home_markdown2 = '''
## Philosophy

- For this prototype, we will assume we have access to appropriate student information.
  -  What information that entails we will fill in as we go.

- For this prototype, we will save the student information in a sqlite3 db to be retrieved in course
- We will keep track of the steps, and show different "Home" pages depending on what has already been filled in by the student. 
- We will also allow the student to navigate to previous steps to update or fix information.
- The most important information is included as tabs in the top of the webpage.

'''

home_markdown1 = '''
# Notes

We need to allow for a view with exploration before someone logs in (suppose this is used by somebody not yet enrolled). We will add additional views for those that are logged in. E.g., completed courses, transfer credits, etc.

_**We assume someone is logged in at this point.**_

_**Need to add a few example students to our DB to demo the web tool.**_

Once logged in, the home page will show important dashboard.


## Tab Steps Above (Currently Disabled)
### Login

1. This is where the notes will go.
1. This is where the notes will go.

### Import information

1. This is where the notes will go.

### Update Information

1. This is where  the notes will go.

### Personalization

1. This is where the notes will go.
'''

sample_markdown = '''
## Notes and To Do's:

To Do:

- Find icons and change them.
- Add dropdown or tab menus for personalization
- Add menus for elective exploration and selection
- Add menus for minor exploration and selection
- Add checkbox or toggle switch for adding completed credits
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code_works = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}
    
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>

  <!-- Load d3.js -->
  <script src='https://d3js.org/d3.v5.js'></script>
</head>

<body>

  <script type="module">
    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 2.25*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {{
        bin.push(bin[k] + 20 + 2.25*boxWidth);
    }}
    
    // Define y coordinates for rectangles
    const yGap = 4;
    const boxSpace = boxHeight + yGap;
    var row = [80];
    for (let k=0; k <=10; k++) {{
        row.push(row[k] + boxSpace);
    }}

    var semesterData = [];
    const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
    for (let year = 2024; year <= 2040; year++) {{
      for (let season of seasons) {{
        semesterData.push(`${{season}} ${{year}}`);
      }}
    }}
    
    function render(data) {{
      // Start Nested Functions
      function drawColumn(period, data) {{
        var filteredData = data.filter(item => item.period === period);
        var anyItem = false;
        for (let j = 0; j < data.length; j++) {{
          let offset = (j % 3 - 1) * sessionOffset;
          let item = filteredData[j];
          if (item !== undefined) {{
            anyItem = true;
            let fullname = `${{item.name}} (${{item.credits}})`;
            drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
          }}
        }}
        if (anyItem) {{
          drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
        }}
      }}
      function drawRectangle(x, y, name, color, textcolor, description='') {{
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
      }}
      function drawHeader(x, y, name, color, textcolor, description='') {{
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
      }}
      // End of Nested Functions
      zoomable.selectAll(".movable").remove();
      var maxPeriod = Math.max(...data.map(item => item.period));
      for (let j = 0; j <= maxPeriod; j++) {{
        drawColumn(j, data);
      }}
    }}

    // Select the body
    var body = d3.select("body");

    // Zoom behavior
    var svg = body.append('svg')
      .attr('id', 'datavizArea')
      .attr('height', 300)
      .attr('width', 900);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
      .on("zoom", function() {{
        zoomable.attr("transform", d3.event.transform);
      }});
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));

    render({data});
  
  </script>

</body>
</html>
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}   
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>
  <script src='https://d3js.org/d3.v5.js'></script>
</head>
<body>
  <script type="module">
    {javascript}
    render({data});
  </script>
</body>
</html>
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
html_code_minimal = '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
      text-align: center;
    }}   
    svg {{
      margin-top: 12px;
      border: 1px solid #aaa;
    }}
  </style>
  <script src='https://d3js.org/d3.v5.js'></script>
</head>
<body>
  <script type="module">
    {javascript}
    render({headers});
    render({data});
  </script>
</body>
</html>
'''

javascript_insert_double = '''
    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 2.25*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {{
        bin.push(bin[k] + 20 + 2.25*boxWidth);
    }}
    
    // Define y coordinates for rectangles
    const yGap = 4;
    const boxSpace = boxHeight + yGap;
    var row = [80];
    for (let k=0; k <=10; k++) {{
        row.push(row[k] + boxSpace);
    }}

    var semesterData = [];
    const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
    for (let year = 2024; year <= 2040; year++) {{
      for (let season of seasons) {{
        semesterData.push(`${{season}} ${{year}}`);
      }}
    }}
    
    function render(data) {{
      // Start Nested Functions
      function drawColumn(period, data) {{
        var filteredData = data.filter(item => item.period === period);
        var anyItem = false;
        for (let j = 0; j < data.length; j++) {{
          let offset = (j % 3 - 1) * sessionOffset;
          let item = filteredData[j];
          if (item !== undefined) {{
            anyItem = true;
            let fullname = `${{item.name}} (${{item.credits}})`;
            drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
          }}
        }}
        if (anyItem) {{
          drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
        }}
      }}
      function drawRectangle(x, y, name, color, textcolor, description='') {{
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
      }}
      function drawHeader(x, y, name, color, textcolor, description='') {{
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
      }}
      // End of Nested Functions
      zoomable.selectAll(".movable").remove();
      var maxPeriod = Math.max(...data.map(item => item.period));
      for (let j = 0; j <= maxPeriod; j++) {{
        drawColumn(j, data);
      }}
    }}

    // Select the body
    var body = d3.select("body");

    // Zoom behavior
    var svg = body.append('svg')
      .attr('id', 'datavizArea')
      .attr('height', 300)
      .attr('width', 900);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
      .on("zoom", function() {{
        zoomable.attr("transform", d3.event.transform);
      }});
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.80).translate(-160, 0));
'''

## javascript_minimal is currently the one being used !!!!
javascript_insert = '''
    const screenWidth = 800;
    const boxWidth = 110;
    const boxHeight = 40;
    const textOffsetX = 10; 
    const textOffsetY = 25;
    const sessionOffset = 60;
    const headerRow = 20;

    // Define x coordinates for rectangles
    var bin = [10];
    // if sessions, then 2.25*boxWidth else boxWidth
    for (let k=0; k <=30; k++) {
        bin.push(bin[k] + 20 + 2.3*boxWidth);
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
'''

# javascript_draw_only takes coordinates from python rather than computing itself in d3
# it is the current implementation

javascript_draw_only = '''
    //const screenWidth = 1200;
    const screenWidth = 800;
    const boxHeight = 40;
    const textOffsetX = 20;
    const textOffsetY = 25;

    function drawRect(x, y, width, printname, color, textcolor, offset, fontsize, description) {
        var g = zoomable.append("g");
        g.append("rect")
            .attr("x", x)
            .attr("y", y)
            .attr("width", width)
            .attr("height", boxHeight)
            .style("fill", color)
            .classed("movable", true); 
        g.append("text")
            .attr("x", x + offset*textOffsetX)
            .attr("y", y + textOffsetY)
            .text(printname)
            .attr("fill", textcolor)
            .style("font-size", fontsize)
            .style("font-family", "Arial")
            .style("font-weight", "bold")
            .classed("movable", true); 
        // Add a tooltip
        g.append("description")
            .text(description);
    }
    function render(data) {
        for (var i = 0; i < data.length; i++) {
            var item = data[i];
            if (item.x === undefined || 
                item.y === undefined ||
                item.width === undefined || 
                item.printname === undefined || 
                item.color === undefined || 
                item.textcolor === undefined ||
                item.offset === undefined ||
                item.fontsize === undefined ||
                item.description === undefined) {
                    console.error('Error: Missing property in item ' + i);
                    continue;
            }
            drawRect(item.x, item.y, item.width, item.printname, item.color, 
                item.textcolor, item.offset, item.fontsize, item.description);
        }
    }

    // Select the body
    var body = d3.select("body");
    // Zoom behavior
    var svg = body.append('svg')
        .attr('id', 'datavizArea')
        .attr('height', 290)
        .attr('width', 690);
    var zoomable = svg.append("g");
    var zoom = d3.zoom()
        .on("zoom", function() {
            zoomable.attr("transform", d3.event.transform);
        });
    svg.call(zoom)
        .call(zoom.transform, d3.zoomIdentity.scale(0.75).translate(0, 0));
'''

## Escape curly brackets {} with {{}} so that substitution within Python works properly
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
for (let k=0; k <=30; k++) {{
    bin.push(bin[k] + 20 + 1.75*boxWidth);
}}
    
// Define y coordinates for rectangles
const yGap = 4;
const boxSpace = boxHeight + yGap;
var row = [80];
for (let k=0; k <=10; k++) {{
    row.push(row[k] + boxSpace);
}}

var semesterData = [];
const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
for (let year = 2024; year <= 2040; year++) {{
  for (let season of seasons) {{
    semesterData.push(`${{season}} ${{year}}`);
  }}
}}
    
function render(data) {{
  // Start Nested Functions
  function drawColumn(period, data) {{
    var filteredData = data.filter(item => item.period === period);
    var anyItem = false;
    for (let j = 0; j < data.length; j++) {{
      let offset = (j % 3 - 1) * sessionOffset;
      let item = filteredData[j];
      if (item !== undefined) {{
        anyItem = true;
        let fullname = `${{item.name}} (${{item.credits}})`;
        drawRectangle(bin[period]+offset, row[j], fullname, item.color, item.textcolor);
      }}
    }}
    if (anyItem) {{
      drawHeader(bin[period], 20, semesterData[period-1], 'lightgray', 'black');
    }}
  }}
  function drawRectangle(x, y, name, color, textcolor, description='') {{
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
  }}
  function drawHeader(x, y, name, color, textcolor, description='') {{
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
  }}
  // End of Nested Functions
  zoomable.selectAll(".movable").remove();
  var maxPeriod = Math.max(...data.map(item => item.period));
  for (let j = 0; j <= maxPeriod; j++) {{
    drawColumn(j, data);
  }}
}}

// Select the body
var body = d3.select("body");

// Zoom behavior
var svg = body.append('svg')
  .attr('id', 'datavizArea')
  .attr('height', 400)
  .attr('width', 800);
var zoomable = svg.append("g");
var zoom = d3.zoom()
  .on("zoom", function() {{
    zoomable.attr("transform", d3.event.transform);
  }});
svg.call(zoom);
'''

d3_template = '''
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

<body style="margin:0; padding:0">
  <script src="{script}"></script>
  <script>render({data})</script>
</body>
</html>
'''

data_json = [
    {
        "seq": 1,
        "name": "PACE 111B",
        "credits": 3,
        "color": "purple",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1,
    },
    {
        "seq": 2,
        "name": "LIBS 150",
        "credits": 1,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1,
    },
    {
        "seq": 3,
        "name": "WRTG 111",
        "credits": 3,
        "color": "green",
        "textcolor": "white",
        "prerequisite": "",
        "period": 1,
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

## map "term" to "period" using start_term
## allow someone to X out of a term directly

## will make it possible to move from one session to another
## check whether prerequisites in session 1 fulfill session 3 follow up
## also, have warnings for courses that should be taken closely together if we are doing,
##  e.g., period 1 session 1 to period 2 session 3 is a pretty long time
## allow people to x out a session
## 

data_json_new = [
    { "seq":  1, "name": "PACE 111", "credits": 3, "type": "general",  "period":  1, "session": 1, "prerequisite": ""                                },
    { "seq":  2, "name": "LIBS 150", "credits": 1, "type": "general",  "period":  1, "session": 2, "prerequisite": ""                                },
    { "seq":  3, "name": "WRTG 111", "credits": 3, "type": "general",  "period":  1, "session": 3, "prerequisite": ""                                },
    { "seq":  4, "name": "WRTG 112", "credits": 3, "type": "general",  "period":  2, "session": 1, "prerequisite": ""                                },
    { "seq":  5, "name": "NUTR 100", "credits": 3, "type": "general",  "period":  2, "session": 2, "prerequisite": ""                                },
    { "seq":  6, "name": "BMGT 110", "credits": 3, "type": "major",    "period":  3, "session": 3, "prerequisite": ""                                },
    { "seq":  7, "name": "SPCH 100", "credits": 3, "type": "general",  "period":  3, "session": 1, "prerequisite": ""                                },
    { "seq":  8, "name": "STAT 200", "credits": 3, "type": "required", "period":  3, "session": 2, "prerequisite": ""                                },
    { "seq":  9, "name": "IFSM 300", "credits": 3, "type": "required", "period":  4, "session": 1, "prerequisite": ""                                },
    { "seq": 10, "name": "ACCT 220", "credits": 3, "type": "major",    "period":  4, "session": 2, "prerequisite": ""                                }, 
    { "seq": 11, "name": "HUMN 100", "credits": 3, "type": "general",  "period":  4, "session": 3, "prerequisite": ""                                }, 
    { "seq": 12, "name": "BIOL 103", "credits": 4, "type": "general",  "period":  5, "session": 1, "prerequisite": ""                                }, 
    { "seq": 13, "name": "ECON 201", "credits": 3, "type": "required", "period":  5, "session": 3, "prerequisite": ""                                }, 
    { "seq": 14, "name": "ARTH 334", "credits": 3, "type": "general",  "period":  5, "session": 2, "prerequisite": ""                                },
    { "seq": 15, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  6, "session": 1, "prerequisite": ""                                }, 
    { "seq": 16, "name": "ECON 203", "credits": 3, "type": "required", "period":  6, "session": 2, "prerequisite": ""                                }, 
    { "seq": 17, "name": "ACCT 221", "credits": 3, "type": "major",    "period":  7, "session": 1, "prerequisite": "ACCT 220"                        }, 
    { "seq": 18, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  7, "session": 2, "prerequisite": ""                                }, 
    { "seq": 19, "name": "BMGT 364", "credits": 3, "type": "major",    "period":  7, "session": 3, "prerequisite": ""                                }, 
    { "seq": 20, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  8, "session": 2, "prerequisite": ""                                }, 
    { "seq": 21, "name": "BMGT 365", "credits": 3, "type": "major",    "period":  8, "session": 1, "prerequisite": "BMGT 364"                        }, 
    { "seq": 22, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  9, "session": 1, "prerequisite": ""                                }, 
    { "seq": 23, "name": "MRKT 310", "credits": 3, "type": "major",    "period":  8, "session": 3, "prerequisite": ""                                }, 
    { "seq": 24, "name": "WRTG 394", "credits": 3, "type": "general",  "period":  9, "session": 2, "prerequisite": "WRTG 112"                        }, 
    { "seq": 25, "name": "ELECTIVE", "credits": 3, "type": "elective", "period":  9, "session": 3, "prerequisite": ""                                }, 
    { "seq": 26, "name": "BMGT 380", "credits": 3, "type": "major",    "period": 10, "session": 1, "prerequisite": ""                                }, 
    { "seq": 27, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 10, "session": 2, "prerequisite": ""                                }, 
    { "seq": 28, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 11, "session": 1, "prerequisite": ""                                }, 
    { "seq": 29, "name": "HRMN 300", "credits": 3, "type": "major",    "period": 11, "session": 2, "prerequisite": ""                                },
    { "seq": 30, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 11, "session": 3, "prerequisite": ""                                }, 
    { "seq": 31, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 12, "session": 2, "prerequisite": ""                                }, 
    { "seq": 32, "name": "FINC 330", "credits": 3, "type": "major",    "period": 12, "session": 1, "prerequisite": "ACCT 221 & STAT 200"             }, 
    { "seq": 33, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 12, "session": 3, "prerequisite": ""                                }, 
    { "seq": 34, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 13, "session": 1, "prerequisite": ""                                }, 
    { "seq": 35, "name": "BMGT 496", "credits": 3, "type": "major",    "period": 13, "session": 2, "prerequisite": ""                                }, 
    { "seq": 36, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 13, "session": 3, "prerequisite": ""                                }, 
    { "seq": 37, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 14, "session": 1, "prerequisite": ""                                }, 
    { "seq": 38, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 14, "session": 2, "prerequisite": ""                                }, 
    { "seq": 39, "name": "ELECTIVE", "credits": 3, "type": "elective", "period": 15, "session": 1, "prerequisite": ""                                }, 
    { "seq": 40, "name": "BMGT 495", "credits": 3, "type": "major",    "period": 15, "session": 2, "prerequisite": "BMGT 365 & MRKT 310 & FINC 330"  }, 
    { "seq": 41, "name": "CAPSTONE", "credits": 1, "type": "elective", "period": 15, "session": 3, "prerequisite": "FINC 330"                        }, 
]
