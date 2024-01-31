define([
    'backbone',
    'd3',
    'global',
    'axisdaysview',
    'axismonthsview',
    'zoomview',
    'zoommodel',
    'gridview',
], function(Backbone, d3, G,
        AxisDaysView, AxisMonthsView, ZoomView, ZoomModel, GridView) {
    var AppView = Backbone.View.extend({
        el: '#app',

        initialize: function(options) {
            // init canvas
            //
            this.canvas = d3.select('#canvas');
            this.canvas
                .attr('height', G.config.height)
                .attr("width", G.config.width + G.config.margin.left + G.config.margin.right);
            this.canvas.select("#main")
                .attr("transform", "translate(" + G.config.margin.left + "," + G.config.margin.top + ")");

            // init axis canvas
            //
            d3.select('#axis-top')
                .attr("width", G.config.width + G.config.margin.left + G.config.margin.right)
                .attr("height", G.config.axis.height);

            // startup modules
            //
            this.zoomModel = new ZoomModel();

            this.axisDaysView = new AxisDaysView();
            this.axisMonthsView = new AxisMonthsView();
            this.zoomView = new ZoomView({model: this.model, zoomModel: this.zoomModel});
            this.gridView = new GridView({model: this.model});

            d3.select('header').transition().duration(500).delay(500).style('top', '0px');

            G.events.trigger('initialized');
        }
    });

    return AppView;
});