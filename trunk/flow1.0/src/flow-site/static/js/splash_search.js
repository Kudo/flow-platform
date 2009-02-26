search_tabs = function() {
	// Get the tabs
	var $tabs = $("#search-tags a");

	// Hide all (default)
	$tabs.each(function() {
			$tab = $($(this).attr("href"));
			$tab.hide();	
			});

	// Add event listener
	$tabs.mouseover(function() {
			// Remove previous
			$(".chosen").removeClass("chosen");
			$(".showing").hide();

			// Get next
			$tab = $($(this).attr("href"));

			// Show next
			$tab.show().addClass("showing");
			$(this).addClass("chosen");


			e.preventDefault();
			});

	// Show default
	$tabs.eq(0).addClass("chosen");
	$($tabs.eq(0).attr("href")).show().addClass("showing");


}

