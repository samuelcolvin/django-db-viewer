function Graph(query_id, title){
	$('#error').hide();
	this.x_axis = null;
	this.y_axis = null;
	this.title = title;
	
	var raw_data;
	var channels;
	var qurl = csv_url + '?queries=' + query_id;

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
		if (_.contains(channels, 'DATETIME')){
			this.x_axis = _.findKey(channels, function(v){return v=='DATETIME';});
		}
		if (_.contains(channels, 'DOUBLE')){
			this.y_axis = _.findKey(channels, function(v){return v=='DOUBLE';});
		}
		raw_data = csvdata.rows;
		_populate_selects();
	}
	
	this.populate_selects = _populate_selects;
	
	function _populate_selects(){
		$.each(channels, function(value) {
		    $("#x_select").append($("<option />").val(value).text(value));
		    $("#y_select").append($("<option />").val(value).text(value));
		});
		$('#x_select').val(this.x_axis);
		$('#y_select').val(this.y_axis);
    	$('#save').removeAttr('disabled');
	}
	
	this.get_data = function() {
		var xy = [];
		for (var i = 0; i < raw_data.length; i += 1) {
			var r = raw_data[i];
			xy.push({
				x : get_value(r, this.x_axis),
				y : get_value(r, this.y_axis)
			});
		}
		return xy;
	};
	
	function get_value(row, name){
		var v = row[name];
		if (channels[name] == 'DATETIME'){
			v = new Date(v * 1000);
		}
		return v;
	}
}
var live_graph;
$('#add_query').click(function () {
	live_graph = null;
	$('#id_queries').val(-1);
	$('#delete').hide();
    $("#x_select").empty();
    $("#y_select").empty();
	$('#save').attr('disabled', 'disabled');
	$('#id_queries').removeAttr('disabled');
	$('#btn-get-data').removeAttr('disabled');
	$('#edit_model').modal('show');
});

var graphs = {};

$('#btn-get-data').click(function(){
	var query_id = parseInt($('#id_queries').val());
	var name = $('#id_queries option:selected').text();
	live_graph = new Graph(query_id, name);
});

$('#save').click(function() {
	if (live_graph == null){
		return;
	}
	var qid = parseInt($('#id_queries').val());
	if (!_.has(graphs, qid)){
		add_blog(qid, live_graph.title);
	}
	live_graph.x_axis = $('#x_select').val();
	live_graph.y_axis = $('#y_select').val();
	
	graphs[qid] = live_graph;
	draw();
});

function add_blog(id, name){
	var d = $('#template-query').clone();
	d.attr('id', 'query_' + id);
	d.attr('qid', id);
	d.find('.btn').click(blob_edit);
	d.find('.btn').text(name);
	d.appendTo($('#query-panel'));
}

function blob_edit(){
	var qid = set_live_graph(this);
	live_graph.populate_selects();
	$('#id_queries').val(qid);
	$('#delete').show();
	$('#id_queries').attr('disabled', 'disabled');
	$('#btn-get-data').attr('disabled', 'disabled');
	$('#edit_model').modal('show');
	return close_dropdown(this);
}

function blob_delete(){
	var qid = set_live_graph(this);
	delete graphs[qid];
	$('#query_' + qid).remove();
	draw();
	return close_dropdown(this);
}

function set_live_graph(t){
	var blog = $(t).closest('.query-blob');
	var qid = parseInt(blog.attr('qid'));
	live_graph = graphs[qid];
	return qid;
}

function close_dropdown(t){
	$(t).closest('ul').dropdown('toggle');;
	return false;	
}

function draw(){
	if (live_graph != null){
		var plot = new Plot();
		_.forEach(graphs, function(graph){
			plot.add_series(graph.get_data());
			if (plot.title != ''){
				plot.title += ', ';
			}
			plot.title += graph.title;
		});
		plot.draw();
	}
}

function resize(){
	$('#chart-area').height($(window).height() - $('#chart-area').position().top - 10);
	draw();
}

resize();
$(window).resize(resize);

