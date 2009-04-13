/**
 * NPO News edit function for \templates\nponpo_home.html
 * @author potato
 */

$(document).ready(function(){
	var btn_flag = 0; //initial value, 1: Modify
	var input_temp = '';
	
	$("#npo_edit_button").click(function() {
	  if ( btn_flag == 0 ) {
		var npo_news_temp_1 = $("#npo_news_1").text();
	    $("#npo_news_1").html("<input id='npo_news_1_input' name='npo_news_1' type='text' size='48' value='"+ npo_news_temp_1 +"'>");	  	
		var npo_news_temp_2 = $("#npo_news_2").text();
	    $("#npo_news_2").html("<input id='npo_news_2_input' name='npo_news_2' type='text' size='48' value='"+ npo_news_temp_2 +"'>");	 
		var npo_news_temp_3 = $("#npo_news_3").text();
	    $("#npo_news_3").html("<input id='npo_news_3_input' name='npo_news_3' type='text' size='48' value='"+ npo_news_temp_3 +"'>");
		$("#npo_edit_button").hide();
		$("#npo_edit_button_ok").show();
		btn_flag = 1;
	  }
	 }); // End of btn_news_1 click function

	$("#npo_edit_button_ok").click(function() {
	  if ( btn_flag == 1 ) {
	    npo_news_temp_1 = $("#npo_news_1_input").val();
		npo_news_temp_2 = $("#npo_news_2_input").val();
		npo_news_temp_3 = $("#npo_news_3_input").val();
		$("#npo_news_1").html('<span id="npo_news_1">'+ npo_news_temp_1 +'</span>');	  
		$("#npo_news_2").html('<span id="npo_news_2">'+ npo_news_temp_2 +'</span>');	
		$("#npo_news_3").html('<span id="npo_news_3">'+ npo_news_temp_3 +'</span>');		
		$("#npo_edit_button").show();
		$("#npo_edit_button_ok").hide();
		btn_flag = 0;
	  }
	 }); // End of btn_news_1_ok click function	  
	 
})// End of (document).ready function.



	/**
	 * @param {jQuery} $target 	,ex:var $target = $('#data-table');
	 * @param {String} url		,ex:var url = (ON_LINE) ? ON_LINE_URL : OFF_LINE_URL;	
	 * @param {String} data		,ex:var request = { name: "potato", time: "2:00 pm" };
	 */
	function doAjax($target, url, data)
	{
		$.ajax(
		{
			url: url,
			data: data,
			type: 'POST',
			timeout: 10000,
			contentType: 'application/json',
			dataType: 'json',
			success: function(data)
			{
				alert('Successed');
			},
			error: function()
			{
				alert('Failed');
				return false;
			}
		});
	}


