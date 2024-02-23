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

