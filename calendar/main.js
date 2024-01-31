require.config({
    paths: {
        "jquery": 'http://ajax.googleapis.com/ajax/libs/jquery/2.0.0/jquery.min',
        "underscore": 'http://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.5.1/underscore-min',
        "backbone": 'http://cdnjs.cloudflare.com/ajax/libs/backbone.js/1.0.0/backbone-min',
        "d3": 'http://cdnjs.cloudflare.com/ajax/libs/d3/3.1.6/d3.min',
        "d3.lambdas": 'd3.lambdas'
    },
    shim: {
        "underscore": { exports: '_' },
        "backbone": { deps: ["underscore", "jquery"], exports: "Backbone" },
        "d3": { exports: 'd3' },
        "d3.lambdas": [ 'd3' ]
    }
});

require(['appview'], function(AppView) {
    new AppView();
});