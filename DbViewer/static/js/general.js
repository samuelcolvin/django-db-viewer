$('.confirm-follow').click(function(e) {
    var link = $(this).attr('href');
    e.preventDefault();    
    bootbox.confirm($(this).attr('msg'), function(result) {    
        if (result) {
            document.location.href = link;
        }    
    });
});

$('#id_filter').change(
    function(){
         $('.filter-form').submit();
});

$('.pop-icon').click(function(e){
	window.open($(this).attr('href'),'name','height=600,width=800');
	return false;
});