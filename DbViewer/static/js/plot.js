function Plot(){
	var chart;
	var data = [];
	this.title = '';
	this.x_title = 'X';
	this.y_title = 'Y';
	
	this.add_series = function(xy) {
		data.push({ type : 'line', 'dataPoints': xy });
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
			data : data,
		});
		chart.render();
	};
}