define([
    'jquery',
    'underscore',
    'backbone',
    'd3'
], function($, _, Backbone, d3) {
    var Global = {

        config: {},

        initialize: function() {
            this.initDimensions();
            this.initD3();
            this.initTimescale();

            this.events = _.extend({}, Backbone.Events);
        },

        initDimensions: function() {
            this.config.margin = { top: 95, right: 0, bottom: 50, left: 0 };
            this.config.width = $(window).width() - this.config.margin.left - this.config.margin.right;
            this.config.height = 500;
        },

        initD3: function() {
            var self = this;
            this.config.durationNormal = 300;
            this.config.duration = this.config.durationNormal;

            // axis
            //
            this.config.axis = {};
            this.config.axis.height = 50;
            // should to be sorted from high to low values
            this.config.axis.ticks = {
                longDays: 240,
                shortDays: 112,
                weeks: 40,
                months: 0
            };
        },

        initTimescale: function() {
            // today based timescale
            var today = new Date(),
                magicNumber = 1.5,
                days = Global.config.width / (this.config.axis.ticks.shortDays/7) / magicNumber;
            this.timeScale = d3.time.scale()
                .domain([d3.time.day.offset(today, -0.6 * days),
                         d3.time.day.offset(today, 0.4 * days)])
                .rangeRound([0, Global.config.width]);
        },

        utils: {
            daysToPixels: function(days, timeScale) {
                var d1 = new Date();
                timeScale || (timeScale = Global.timeScale);
                return timeScale(d3.time.day.offset(d1, days)) - timeScale(d1);
            } // daysToPixels

        }
    };

    Global.initialize();

    return Global;
});
