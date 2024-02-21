import sys
import traceback
from h2o_wave import Q, expando_to_dict, ui, graphics as g

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

# A meta card to hold the app's title, layouts, dialogs, theme and other meta information
meta = ui.meta_card(
    box='',
    title='UMGC Wave App',
    theme='ember',
    layouts=[
        ui.layout(
            breakpoint='xs',
            min_height='100vh',
#           max_width='1200px',
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

toggle = ui.form_card(box='rightgrid', items=[
    ui.toggle(name='toggle', label='Transfer Credits', value=False, disabled=False),
])

footer = ui.footer_card(
    box='footer',
    caption='Made using [H2O Wave](https://wave.h2o.ai).'
)

markdown = ui.form_card(
    box='rightnote',
    items=[ui.text(sample_markdown)]
)

#image_path, = await q.site.upload(['umgc-logo.png'])

def header(image_path):
    result = ui.header_card(    
        box='header',
        title='UMGC Curriculum Assistant',
        subtitle="Title TBD",
        image=image_path,
        items=[ui.textbox(name='textbox_default', label='Student Name', value='John Doe', disabled=True)]
    )
    return result

def d3plot(html):
    result = ui.frame_card(
        box=ui.box('midgrid', height='600px', width='1000px'),
        title='Tentative Course Schedule',
        content=html
    )
    return result

def stats(D):
    result = ui.form_card(
        box='horizontal', items=[
            ui.stats(justify='between', items=[
                ui.stat(label='Credits', 
                        value=str(D['total_credits_remaining']), 
                        caption='Credits Remaining', 
                        icon='Education'),            
                ui.stat(label='Tuition', 
                        value=D['next_term_cost'], 
                        caption='Estimated Tuition', 
                        icon='Money'),
                ui.stat(label='Terms Remaining', 
                        value=str(D['terms_remaining']), 
                        caption='Terms Remaining', 
                        icon='Education'),
                ui.stat(label='Finish Date', 
                        value=D['completion_date'], 
                        caption='(Estimated)', 
                        icon='SpecialEvent'),
                ui.stat(label='Total Tuition', 
                        value=D['total_cost_remaining'], 
                        caption='Estimated Tuition', 
                        icon='Money'),
            ])
        ]
    )

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

#    q.page['tall_stats'] = ui.tall_stats_card(
##        box=ui.box('right2', height='200px',),
#        box=ui.box('left2'),
#        items=[
#            ui.stat(label='FINISH DATE', value=completion_date),
#            ui.stat(label='TERMS REMAINING', value=str(terms_remaining)),
#            ui.stat(label='CREDITS LEFT', value=str(total_credits_remaining)), 
#        ]
#    )

#menu_width = '250px'
#
#dropdown_menus = ui.form_card(
#    box='horizontal',
#    items=[
#        ui.inline(
#            items=[
#                ui.dropdown(
#                    name='degree', 
#                    label='Degree', 
#                    value=q.args.degree,
#                    trigger=True,
#                    width=menu_width,
#                    choices=[
#                        ui.choice(name='AS', label="Associate"),
#                        ui.choice(name='BS', label="Bachelor's"),
#                        ui.choice(name='MS', label="Master's"),
#                        ui.choice(name='DC', label="Doctorate"),
#                        ui.choice(name='UC', label="Undergraduate Certificate"),
#                        ui.choice(name='GC', label="Graduate Certificate")
#                ]),
#                ui.dropdown(
#                    name='area_of_study', 
#                    label='Area of Study', 
#                    value=q.args.area_of_study,
#                    trigger=False,
#                    disabled=False,
#                    width=menu_width,
#                    choices=[
#                        ui.choice(name='BM', label='Business & Management'),
#                        ui.choice(name='CS', label='Cybersecurity'),
#                        ui.choice(name='DA', label='Data Analytics'),
#                        ui.choice(name='ET', label='Education & Teaching'),
#                        ui.choice(name='HS', label='Healthcare & Science'),
#                        ui.choice(name='LA', label='Liberal Arts & Communications'),
#                        ui.choice(name='PS', label='Public Safety'),
#                        ui.choice(name='IT', label='IT & Computer Science')
#                ]),
#                ui.dropdown(
#                    name='major', 
#                    label='Major', 
#                    value=q.args.major,
#                    trigger=False,
#                    disabled=False,
#                    width=menu_width,
#                    choices=[
#                        ui.choice(name='AC', label='Accounting'),
#                        ui.choice(name='BA', label='Business Administration'),
#                        ui.choice(name='FI', label='Finance'),
#                        ui.choice(name='HR', label='Human Resource Management'),
#                        ui.choice(name='MS', label='Management Studies'),
#                        ui.choice(name='MK', label='Marketing'),
#                ]),
#            ]
#        )
#    ]
#)
#