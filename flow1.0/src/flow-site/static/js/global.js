$(document).ready(function() {
    // If get image failed, load default image instead
    $("img").error(function () {
      $(this).unbind("error").attr("src", "/static/images/head_blue50.jpg");
    });
    position_search_bar();
});
