define([
    'backbone',
    'd3',
    'global'
], function(Backbone, d3, G) {
    var ZoomView = Backbone.View.extend({
        el: '#canvas .background',

        initialize: function(options) {
            var self = this;
            this.zoomModel = options.zoomModel;

            // init background rect
            //
            this.d3 = d3.select(this.el)
                .attr("width", G.config.width + G.config.margin.left + G.config.margin.right)
                .attr("height", G.config.height + G.config.margin.top + G.config.margin.bottom)
                .on("dblclick", function() { self.zoomModel.zoom(d3.select('#canvas .background').node()); })
                .on("mousedown", function() { self.mousedown(); } );
        },

        // start panning
        //
        mousedown: function() {
            if (d3.event.button !== 0) return;
            var zoomModel = this.zoomModel,
                panWorker = this.zoomModel.startPan(d3.event.target),
                w = d3.select(window)
                    .on('mousemove.pan', function mousemove() { panWorker(); })
                    .on('mouseup.pan', function mouseup() {
                        if (zoomModel.moved) {
                            d3.event.preventDefault();
                        }
                        w.on("mousemove.pan", null).on("mouseup.pan", null);
                    });
            d3.event.preventDefault();
            window.focus();
        } // mousedown
    });

    return ZoomView;
});