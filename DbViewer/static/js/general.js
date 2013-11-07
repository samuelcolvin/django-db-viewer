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