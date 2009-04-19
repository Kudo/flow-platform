$(document).ready(function() {
    // If get image failed, load default image instead
    $("img").error(function () {
      $(this).unbind("error").attr("src", "/static/images/volunteer50.gif");
    });
    position_search_bar();
});
