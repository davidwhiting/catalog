function _(e){const n={className:"string",variants:[e.inherit(e.QUOTE_STRING_MODE,{begin:'((u8?|U)|L)?"'}),{begin:'(u8?|U)?R"',end:'"',contains:[e.BACKSLASH_ESCAPE]},{begin:"'\\\\?.",end:"'",illegal:"."}]},a={className:"number",variants:[{begin:"\\b(\\d+(\\.\\d*)?|\\.\\d+)(u|U|l|L|ul|UL|f|F)"},{begin:e.C_NUMBER_RE}],relevance:0},c={className:"meta",begin:"#",end:"$",keywords:{keyword:"if else elif endif define undef ifdef ifndef"},contains:[{begin:/\\\n/,relevance:0},{beginKeywords:"include",end:"$",keywords:{keyword:"include"},contains:[e.inherit(n,{className:"string"}),{className:"string",begin:"<",end:">",illegal:"\\n"}]},n,e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE]},s={className:"variable",begin:/&[a-z\d_]*\b/},i={className:"keyword",begin:"/[a-z][a-z\\d-]*/"},t={className:"symbol",begin:"^\\s*[a-zA-Z_][a-zA-Z\\d_]*:"},o={className:"params",relevance:0,begin:"<",end:">",contains:[a,s]},r={className:"title.class",begin:/[a-zA-Z_][a-zA-Z\d_@-]*(?=\s\{)/,relevance:.2},E={className:"title.class",begin:/^\/(?=\s*\{)/,relevance:10},d={match:/[a-z][a-z-,]+(?=;)/,relevance:0,scope:"attr"},l={relevance:0,match:[/[a-z][a-z-,]+/,/\s*/,/=/],scope:{1:"attr",3:"operator"}},N={scope:"punctuation",relevance:0,match:/\};|[;{}]/};return{name:"Device Tree",contains:[E,s,i,t,r,l,d,o,e.C_LINE_COMMENT_MODE,e.C_BLOCK_COMMENT_MODE,a,n,c,N,{begin:e.IDENT_RE+"::",keywords:""}]}}export{_ as default};