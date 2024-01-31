*Hint: Use `double click` to **zoom in** and `shift + double click` to **zoom out**.*


I was using require.js and backbone.js and therefore there is a lot of extra code here.
So I will highlight the most useful parts.

There is a few features I want to share:  

 * Axis labels between ticks
 * Sticky month names that remain visible at any zoom level
 
Labels between ticks
---
This feature was implemented in the `axisdaysview.js`.  
At first it is called `this.axis` as usual and then text labels are moved to the half-of-the-day:

    this.d3
       .call(this.axis)
       .call(this.adjustTextLabels);

Here is `adjustTextLabels` function:

    adjustTextLabels: function(selection) {
        selection.selectAll('.major text')
            .attr('transform', 'translate(' + G.utils.daysToPixels(1) / 2 + ',0)');
    }

The `daysToPixels` calculates the width of the day (or days) in pixels depending on the current scale. Function defined in the `global.js`:
    
    daysToPixels: function(days, timeScale) {
        var d1 = new Date();
        timeScale || (timeScale = Global.timeScale);
        return timeScale(d3.time.day.offset(d1, days)) - timeScale(d1);
    }

Sticky months
---
Sticky months are implemented in the `axismonthsview.js` in the `renderMonthNames`.  
The `getVisibleMonths` returns an array of the months to be drawn.  
The `setTextPosition` trying to align the name of the month to the center and applies simple maths to leave the month name at the scene as long as possible.