function Graph(query_id, name){
	$('#error').hide();
	
	var qurl = csv_url + '?queries=' + query_id;
	
	var channels;
	var raw_data;
	var chart;

	$.ajax(qurl, {
	    success: function(data) {
	        var csvdata = csvjson.csv2json(data);
	        process_csv(csvdata);
	    },
	    error: function() {
			$('#error').show();
			$('#error').html('Error Loading CSV file');
	    }
	});
	
	function process_csv(csvdata){
		channels = {};
		_.forEach(csvdata.headers, function(h){
			start = h.lastIndexOf('(') + 1;
			finish = h.lastIndexOf(')');
			type = h.substr(start, finish - start);
			channels[h] = type;
		});
		var x_col = null;
		var y_col = null;
		if (_.contains(channels, 'DATETIME')){
			x_col = _.findKey(channels, function(v){return v=='DATETIME';});
		}
		if (_.contains(channels, 'DOUBLE')){
			y_col = _.findKey(channels, function(v){return v=='DOUBLE';});
		}
		raw_data = csvdata.rows;
		populate_selects(x_col, y_col);
		if (x_col != null && y_col != null){
			_draw(x_col, y_col);
		}
	}
	
	function populate_selects(x_col, y_col){
		$.each(channels, function(value) {
		    $("#x_select").append($("<option />").val(value).text(value));
		    $("#y_select").append($("<option />").val(value).text(value));
		});
		$('#x_select').val(x_col);
		$('#y_select').val(y_col);
	}
	
	this.draw = function(x_col, y_col){
		_draw(x_col, y_col);
	};
	
	function _draw(x_col, y_col){
		var xy = [];
		for (var i = 0; i < raw_data.length; i += 1) {
			var r = raw_data[i];
			xy.push({
				x : get_value(r, x_col),
				y : get_value(r, y_col)
			});
		}
		var data = [{ type : 'line', 'dataPoints': xy }];
		// console.log(data);
		populate(data, x_col, y_col);
	}
	
	function get_value(row, name){
		var v = row[name];
		if (channels[name] == 'DATETIME'){
			v = new Date(v * 1000);
		}
		return v;
	}
	
	function populate(data, x_title, y_title){
		$('#chart-area').empty();
		chart = new CanvasJS.Chart('chart-area', {
			zoomEnabled : true,
			backgroundColor: 'inherit',
			title : {
				text : name,
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
				title: x_title
			},
			axisY : {
				includeZero : false,
				labelFontColor: 'white',
				titleFontColor: 'white',
				lineColor: 'white',
				labelFontSize: 16,
				titleFontSize: 18,
				title: y_title
			},
			data : data,
		});
		chart.render();
	}
}
var graph;

function redraw(){
	if (typeof(graph) != 'undefined'){
		graph.draw($('#x_select').val(), $('#y_select').val());
	}
}

function resize(){
	$('#chart-area').height($(window).height() - $('#chart-area').position().top - 10);
	redraw();
}

$('#btn-get-data').click(function(e){
	var query_id = parseInt($('#id_queries').val());
	var name = $('#id_queries option:selected').text();
	graph = new Graph(query_id, name);
});
resize();
$('#x_select').on('change', redraw);
$('#y_select').on('change', redraw);
$(window).resize(resize);
