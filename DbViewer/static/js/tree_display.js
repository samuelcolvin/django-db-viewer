var desc = $('#description');

$('#tree').bind(
    'tree.click',
    function(event) {
        var node = event.node;
        if (typeof(node.info) !== 'undefined'){
	        desc.empty();
	        node.info.forEach(function(info){
	        	desc.append('<h4>' + info[0] + '</h4>');
	        	info[1].forEach(function(prop){
		        	desc.append('<dt>' + prop[0] + '</dt>');
		        	var value = $('<div/>').text(prop[1]).html();
		        	desc.append('<dd><pre>' + value + '</pre></dd>');
	        	});
	        });
        }
    }
);

// function get_data(url){
	// $.getJSON(url, function(data) {
		// $('#tree').tree({data: data});
	// });
// }

$('#tree').tree();

var editor = ace.edit('editor');
document.getElementById('editor').style.fontSize='14px';
editor.setTheme('ace/theme/twilight');
editor.getSession().setMode('ace/mode/sql');
editor.getSession().setUseWrapMode(true);

editor.setValue($('#id_code').val());

editor.on('change', function(e){
	$('#id_code').val(editor.getValue());
});

var main_height = $(window).height() - 80;
$('.column').height(main_height);
$('#editor').height(main_height - 241);

$('#id_filters').on('change', function(e){
	$('.filter-form').submit();
});