function Plot(){
	var chart;
	var data = [];
	this.title = '';
	this.x_title = 'X';
	this.y_title = 'Y';
	
	this.add_series = function(xy, series_title) {
		data.push({ 'type' : 'line', 
					'dataPoints': xy, 
					'name': series_title, 
					'legendText': series_title, 
					'showInLegend': true
				});
	};
	
	this.draw = function(){
		$('#chart-area').empty();
		chart = new CanvasJS.Chart('chart-area', {
			zoomEnabled : true,
			backgroundColor: 'inherit',
			title : {
				text : this.title,
				fontColor: 'white',
				fontSize: 22,
			},
			axisX : {
				labelFontColor: 'white',
				titleFontColor: 'white',
				lineColor: 'white',
				labelFontSize: 16,
				titleFontSize: 18,
				margin: 0,
				title: this.x_title
			},
			axisY : {
				includeZero : false,
				labelFontColor: 'white',
				titleFontColor: 'white',
				lineColor: 'white',
				labelFontSize: 16,
				titleFontSize: 18,
				title: this.y_title
			},
			legend:{
				fontColor: 'white',
				fontSize: 14,
			},
			data : data,
		});
		chart.render();
		$('#chart-area').find('button').addClass('btn btn-default');
		$('#chart-area').find('button').css('margin-left', '10px');
	};
}