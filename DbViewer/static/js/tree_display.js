var desc = $('#description');

var editor = ace.edit('editor');
editor.setTheme('ace/theme/twilight');
// editor.getSession().setMode('ace/mode/sql');
editor.getSession().setUseWrapMode(true);
$('#editor').css({'font-size': '14px'});

function set_editor_format(e){
	var id = parseInt($('#id_db').val());
	var format = _.find(code_formats, {'id': id});
	if (typeof(format) != 'undefined'){
		editor.getSession().setMode('ace/mode/' + format.format);
		$('#format-string').text('(' + format.format + ')');
	}
}
$('#id_db').on('change', set_editor_format);
//$(document).ready(set_editor_format);

function str2html(str){
	var re = new RegExp('\n', 'g');
	return '<p>' + str.replace(re,'</p>\n<p>') + '</p>';
}

$.getJSON($('#tree').attr('data-url'), function(data) {
	$('#tree').tree({data: data.DATA});
	if (typeof(data.ERROR) != 'undefined')
	{
		$('#error').show();
		$('#error').html(str2html(data.ERROR));
	}
});

editor.setValue($('#id_code').val());

editor.on('change', function(e){
	$('#id_code').val(editor.getValue());
});

var main_height = $(window).height() - 80;
$('.column').height(main_height);
// $('#editor').height(main_height - 241);

$('#id_queries').on('change', function(e){
	$('.query-form').submit();
});

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

set_editor_format();