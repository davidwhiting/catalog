define([
    'd3',
    'global',
    'backbone'
], function(d3, G, Backbone) {
    var AxisDaysView = Backbone.View.extend({

        initialize: function() {
            // init axis
            //
            this.d3 = d3.select('#axis-top .axis.days')
                .attr("transform", "translate(" + G.config.margin.left + "," + (G.config.axis.height-1) + ")");
            this.axis = d3.svg.axis()
                .scale(G.timeScale)
                .tickSize(0,0,0)
                .orient("top");

            // init handlers
            //
            this.listenTo(G.events, 'initialized', this.render);
            this.listenTo(G.events, 'zoomed', this.render);
            this.listenTo(G.events, 'panned', this.adjustPan);
        },

        render: function() {
            this.adjustTimeAxis();
            this.d3
                .transition().duration(G.config.duration)
                .call(this.axis)
                .call(this.adjustTextLabels);
        }, // render

        adjustTimeAxis: function() {
            switch(this.getZoomState()) {
                case 'longDays':
                    this.axis
                        .ticks(d3.time.days, 1)
                        .tickFormat(function(d) { return d3.time.format('%a %e')(d); })
                        .tickSubdivide(false);
                    break;
                case 'shortDays':
                    this.axis
                        .ticks(d3.time.days, 1)
                        .tickFormat(function(d) { return d3.time.format('%e')(d); })
                        .tickSubdivide(false);
                    break;
                case 'weeks':
                    this.axis
                        .ticks(d3.time.mondays, 1)
                        .tickFormat(null)
                        .tickSubdivide(6);
                    break;
                default:
                    this.axis
                        .ticks(d3.time.months, 1)
                        .tickFormat(null)
                        .tickSubdivide(1);
            }
        }, // adjustTimeAxis

        adjustTextLabels: function(selection) {
            selection.selectAll('.major text')
                .attr('transform', 'translate(' + G.utils.daysToPixels(1) / 2 + ',0)');
        }, // adjustTextLabels

        adjustPan: function() {
            this.d3
                .call(this.axis)
                .call(this.adjustTextLabels);
        }, // adjustPan

        getZoomState: function() {
            var delta = G.utils.daysToPixels(7);
            return d3.entries(G.config.axis.ticks).filter(function(e) { return e.value <= delta; })[0].key;
        } // getZoomState
    });

    return AxisDaysView;
});
