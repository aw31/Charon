$(document).ready(function() {
    // highlights current tab in blue
    var activeurl =  window.location.pathname;
    $('a[href="'+activeurl+'"]').parent('li').addClass('active');

});

$(":submit").click(function() {
    // disables submit button after single click
    $(":submit").attr('disabled','disabled');
    $("form").submit();
});
