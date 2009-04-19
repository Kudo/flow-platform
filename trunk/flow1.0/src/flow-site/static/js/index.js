// JScript File
var isSearchPanelShowing = false;
var searchPanelActivePage = "Activity";

function jsToggleSearchPanel() {
  isSearchPanelShowing = !isSearchPanelShowing;
  if (isSearchPanelShowing) {
    jsShowSearchPanel();
  } else {
    jsCloseSearchPanel();
  }
}

function jsShowSearchPanel(){
    jsSwitchType(searchPanelActivePage);
	$("#Search_Wrap").fadeIn(200);
}
function jsCloseSearchPanel(){
	$("#Search_Wrap").fadeOut(200);
}
function jsSwitchType(strType){
	$("#Type_Activity").show();

	$(".types").removeClass("selected").addClass("type");
	$(".searches").hide();
    switch (strType)
    { 
        case "Activity":
        	$("#Type_Activity").removeClass("type").addClass("selected");
        	$("#Search_Activity").show();
            break;
        case "Volunteer":
        	$("#Type_Volunteer").removeClass("type").addClass("selected");
        	$("#Search_Volunteer").show();
            break;
        case "Group":
        	$("#Type_Group").removeClass("type").addClass("selected");
        	$("#Search_Group").show();
            break;
        default:
            return;
    } 
	searchPanelActivePage = strType;
}