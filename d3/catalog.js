const d3 = require('d3');

d3.json('data.json').then(data => {
  // Create a SVG container
  const svg = d3.select('body').append('svg')
    .attr('width', 800)
    .attr('height', 600);

  // Create blocks
  const blocks = svg.selectAll('rect')
    .data(data)
    .enter().append('rect')
    .attr('x', (d, i) => i * 30)  // Position blocks
    .attr('y', 50)
    .attr('width', 20)
    .attr('height', 20)
    .attr('fill', d => d.color)  // Color blocks
    .call(d3.drag()  // Make blocks draggable
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  	function dragstarted(event, d) {
  	  d3.select(this).raise().classed('active', true);
  	}
	
  	function dragged(event, d) {
  	  d3.select(this).attr('x', event.x).attr('y', event.y);
  	}
	
  	function dragended(event, d) {
  	  d3.select(this).classed('active', false);
  	}

  	// Create timeSlots
	const timeSlots = Array.from({length: 6}, (_, i) => i + 1);  // [1, 2, 3, 4, 5, 6]
	
	const slotGroups = svg.selectAll('g')
	  .data(timeSlots)
	  .enter().append('g')
	  .attr('transform', (d, i) => `translate(${i * 130 + 50}, 400)`);
	
	slotGroups.append('rect')
	  .attr('width', 100)
	  .attr('height', 100)
	  .attr('stroke', 'black')
	  .attr('fill', 'none');
	
	slotGroups.append('text')
	  .text(d => `Slot ${d}`)
	  .attr('y', -10);


});


