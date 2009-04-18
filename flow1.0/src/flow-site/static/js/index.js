// JScript File
function jsShowSearchPanel(){
    jsSwitchType("Activity");
	$("#Search_Wrap").slideDown(1000);
}
function jsCloseSearchPanel(){
	$("#Search_Wrap").slideUp(1000);
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
    } 
}