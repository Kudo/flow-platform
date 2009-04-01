// JScript File
function jsShowSearchPanel(){
	$("#Search_Wrap").show();
    jsSwitchType("Activity");
}
function jsCloseSearchPanel(){
	$("#Search_Wrap").hide();
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