define([
    'd3',
    'global',
    'd3.lambdas'
], function(d3, G) {
    var AxisMonthsView = Backbone.View.extend({
        el: '#axis-top .axis.months',

        initialize: function() {
            this.d3 = d3.select(this.el)
                .attr('transform', 'translate(' + G.config.margin.left + ', 0)');
            this.d3.append('g')
                .attr('class', 'month-names')
                .attr('transform', 'translate(0, ' + (G.config.axis.height - 2) + ')');

            this.listenTo(G.events, 'zoomed panned', this.render);
            this.render('initial');
        }, // initialize

        render: function(eventType) {
            this.renderMonthNames(eventType);
        }, // render

        renderMonthNames: function(eventType) {
            var self = this,
                scale1 = G.timeScale.copy(),
                scale0 = this.renderMonthNames.scale || scale1,
                data = this.getVisibleMonths(G.timeScale.domain()),
                name = this.d3.select('.month-names').selectAll('.name').data(data, d3.ƒ('getTime')),
                nameEnter, nameUpdate, nameExit,
                text, textEnter, textUpdate;

            this.renderMonthNames.scale = scale1;

            nameEnter = name.enter();
            nameUpdate = name;
            nameExit = name.exit();

            // ENTER
            //
            nameEnter
                .append('text')
                .attr('class', 'name')
                .text(function(d) { return d3.time.format('%B')(d); })
                .call(this.setTextPosition, scale0);

            switch(eventType) {
                case 'initial':
                    // set text position in the other thread
                    // because we need BBox of the already rendered text element
                    setTimeout(function() {
                        self.d3.select('.month-names').selectAll('.name').call(self.setTextPosition, scale0);
                    }, 1);
                    break;
                case 'zoomed':
                    nameUpdate = nameUpdate.transition().duration(G.config.duration);
                    nameExit = nameExit.transition().duration(G.config.duration);
                    break;
            }

            // UPDATE
            // 
            nameUpdate
                .call(this.setTextPosition, scale1);

            // EXIT
            //
            nameExit
                .attr('opacity', 1e-6)
                .call(this.setTextPosition, scale1)
                .remove();
        }, // renderMonthNames


        setTextPosition: function(selection, scale) {
            selection.each(function(d) {
                var width = this.getBBox().width,
                    nextMonthPos = scale(d3.time.month.offset(d, 1)),
                    padding = 3,
                    minPos = 0, maxPos = scale.range()[1],
                    x, opacity;

                x = scale(d) + G.utils.daysToPixels(15) - width / 2; // center
                x = Math.max(minPos, x); // left-left
                x = Math.min(x, nextMonthPos - width - padding);  // left-right

                x = Math.min(x, maxPos - width); // right-right
                x = Math.max(x, scale(d) + padding); // right-left

                if (x < minPos) {
                    opacity = (x + width - minPos) / width;
                } else if (x + width > maxPos) {
                    opacity = (maxPos - x) / width;
                } else {
                    opacity = 1;
                }

                d3.transition(d3.select(this))
                    .attr('x', x)
                    .attr('opacity', opacity);
            });
        }, // setTextPosition


        // d3.time.months could not be used here because of ceil dates
        // that shrink the range. 
        // In this function we need the extended range
        //
        getVisibleMonths: function(domain) {
            var time = d3.time.month.floor(domain[0]),
                end = d3.time.month.floor(domain[1]),
                times = [ time ];
            while(time < end) {
                time = d3.time.month.offset(time, 1);
                times.push(time);
            }
            return times;
        } // getVisibleMonths
    });

    return AxisMonthsView;
});