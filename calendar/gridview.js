define([
    'd3',
    'global',
    'backbone'
], function(d3, G, Backbone) {
    var GridView = Backbone.View.extend({
        el: '#grid',

        initialize: function() {
            this.d3 = d3.select(this.el)
                .attr("transform", "translate(" + G.config.margin.left + ",0)");

            this.listenTo(G.events, 'initialized', this.initAxis);
            this.listenTo(G.events, 'initialized', this.render);
            this.listenTo(G.events, 'zoomed', this.render);
            this.listenTo(G.events, 'panned', this.adjustPan);
        },

        initAxis: function() {
            this.axis = d3.svg.axis().scale(G.timeScale).tickSize(0,0,0);
            var height = G.config.height;
            this.axis
                .tickSize(height, height)
                .tickFormat("");

            this.d3.append('g').attr('class', 'days-ticks');
            this.d3.append('g').attr('class', 'weekends');
            this.d3.append('g').attr('class', 'month-ticks');
        },

        onResize: function() {
            this.render();
        },

        render: function() {
            this.renderGrid.apply(this, arguments);
            this.renderWeekends.apply(this, arguments);
            this.renderMonthTicks.apply(this, arguments);
        }, // render

        renderGrid: function() {
            this.axis.tickSize(G.config.height);
            switch(this.getZoomState()) {
                case 'months':
                    this.axis.ticks(d3.time.months, 1);
                    break;
                default:
                    this.axis.ticks(d3.time.days, 1);
                    break;
            }
            this.d3.select('.days-ticks')
                .transition().duration(G.config.duration)
                .call(this.axis);
        }, // renderGrid

        renderWeekends: function(eventType) {
            var scale1 = G.timeScale.copy(),
                scale0 = this.renderWeekends.scale || scale1,
                domain = scale1.domain(),
                weekend = this.d3.select('.weekends').selectAll('.weekend')
                    .data(d3.time.saturday.range(d3.time.day.offset(domain[0], -2), domain[1]), d3.ƒ('getTime')),
                weekendEnter, weekendUpdate, weekendExit;

            this.renderWeekends.scale = scale1;

            weekendEnter = weekend.enter();
            weekendUpdate = weekend;
            weekendExit = weekend.exit();

            // ENTER
            //
            weekendEnter
                .append('rect')
                .attr('class', 'weekend')
                .attr('y', 0)
                .attr('height', G.config.height)
                .attr('x', function(d) { return scale0(d); })
                .attr('width', G.utils.daysToPixels(2, scale0));

            // UPDATE
            //
            if (eventType == 'zoomed') {
                weekendUpdate = weekend.transition().duration(G.config.duration);
                weekendExit = weekendExit.transition().duration(G.config.duration);
            }

            weekendUpdate
                .attr('height', G.config.height)
                .attr('x', function(d) { return scale1(d); })
                .attr('width', G.utils.daysToPixels(2));

            // EXIT
            //
            weekendExit
                .attr('x', function(d) { return scale1(d); })
                .attr('width', G.utils.daysToPixels(2))
                .remove();

        }, // renderWeekends

        renderMonthTicks: function(eventType) {
            var data = G.timeScale.ticks(d3.time.months),
                tick = this.d3.select('.month-ticks').selectAll('.tick').data(data, d3.ƒ('getTime')),
                tickEnter, tickUpdate, tickExit,
                scale1 = G.timeScale.copy();
                scale0 = this.renderMonthTicks.scale || scale1;

            this.renderMonthTicks.scale = scale1;

            tickEnter = tick.enter().append('line');
            tickUpdate = tick;
            tickExit = tick.exit();
            if (eventType == 'zoomed') {
                tickUpdate = tick.transition().duration(G.config.duration);
                tickExit = tickExit.transition().duration(G.config.duration);
            }

            // ENTER
            //
            tickEnter
                .attr('class', 'tick')
                .attr('y2', G.config.height)
                .attr('transform', function(d) { return 'translate(' + scale0(d) + ', 0)'; });

            // UPDATE
            //
            tickUpdate
                .attr('transform', function(d) { return 'translate(' + scale1(d) + ', 0)'; })
                .attr('y2', G.config.height);

            // EXIT
            //
            tickExit
                .attr('transform', function(d) { return 'translate(' + scale1(d) + ', 0)'; })
                .remove();
        }, // renderMonthTicks

        adjustPan: function() {
            this.d3.select('.days-ticks').call(this.axis);
            this.renderWeekends.apply(this, arguments);
            this.renderMonthTicks.apply(this, arguments);
        }, // adjustPan

        getZoomState: function() {
            var delta = G.utils.daysToPixels(7);
            return d3.entries(G.config.axis.ticks).filter(function(e) { return e.value <= delta; })[0].key;
        } // getZoomState

    });

    return GridView;
});