$(document).ready(function() {
  var category = 'event';
  if (window.location.pathname.match(/^\/(volunteer|npo|event)\//))
    category = RegExp.$1;
  // Create new feed item
  $("#createFeedItem").click(function(e) {
    e.preventDefault();
    $("#createFeedBox").show().dialog({
      modal: true,
      width: 500,
      height: 500,
      close: function(e, ui) { $("#feedPreview").empty(); $(this).hide().dialog('destroy'); },
      buttons: { "送出": function() {
        $.post("/volunteer/space/article/create", $("#createFeedBox form").serialize(),
          function(data) {
            if (data.statusCode >= 200 && data.statusCode < 300)
              window.location.reload();
            else
              alert('儲存失敗 : ' + data.reason);
          }, "json"
        );
        $(this).dialog("close");
      }},
    });
  });

  // remember feed uri
	$("#feedUriSave").click(function(e) {
    e.preventDefault();
    var feedUri = $("input[name='feedUri']");
    $.post("/volunteer/space/article/saveUri", { feedUri: feedUri.val() },
      function(data) {
        if (data.statusCode >= 200 && data.statusCode < 300)
          alert('儲存成功');
        else
          alert('儲存失敗 : ' + data.reason);
      }, "json"
    );
  });

  // preview feed content
	$("#feedUriParse").click(function(e) {
    e.preventDefault();
    var previewObj = $("#feedPreview");
    previewObj.empty();
    previewObj.append('<img src="/static/images/loading-1.gif" />');
    var feedUri = $("input[name='feedUri']");
    $.get("/feedParser", { feedUri: feedUri.val() },
      function(data) {
        previewObj.empty();
        if (data.statusCode >= 200 && data.statusCode < 300)
        {
          content = '<table border="1">\n';
          $.each(data.entryList, function(i, entry) {
            content += '<tr><td>' + '<input type="checkbox" name="itemList" value="'+ entry.title + ',' + entry.uri + '" /></td>\n';
            content += '<td><a style="text-decoration: underline;" href="' + entry.uri + '">' + entry.title + '</a></td>\n';
            content += '<td>' + entry.summary + '</td>\n';
            content += '</tr>\n';
          });
          content += '</table>\n';
          previewObj.append(content);
        }
        else
        {
          previewObj.append('網址存取失敗');
        }
      }, "json"
    );
  });

  // delete a item
	$(".delItem").click(function(e) {
    e.preventDefault();
    $.getJSON($(this).attr("href"), function(data) {
      if (data.statusCode >= 200 && data.statusCode < 300)
      {
        alert('移除成功');
        window.location.reload();
      }
      else
        alert('移除失敗 : ' + data.reason);
    });
  });
});

