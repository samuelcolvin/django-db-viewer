var limit = 100000;

var y = 0;
var data = [];
var dataSeries = {
	type : "line"
};
var dataPoints = [];
for (var i = 0; i < limit; i += 1) {
	y += (Math.random() * 10 - 5);
	dataPoints.push({
		x : i - limit / 2,
		y : y
	});
}
dataSeries.dataPoints = dataPoints;
data.push(dataSeries);
$('#chart-area').height($(window).height() - $('#chart-area').position().top - 10);

function draw(){
	var chart = new CanvasJS.Chart('chart-area', {
		zoomEnabled : true,
		backgroundColor: 'inherit',
		title : {
			text : 'Stress Test: 100,000 Data Points',
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
			title: 'X title'
		},
		axisY : {
			includeZero : false,
			labelFontColor: 'white',
			titleFontColor: 'white',
			lineColor: 'white',
			labelFontSize: 16,
			titleFontSize: 18,
			title: 'Y title'
		},
		data : data,
	});
	chart.render();
}



