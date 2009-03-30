// JScript File
function jsInit(){
    document.getElementById("Search_Wrap").style.display = "none";
}
function jsShowSearchPanel(){
    document.getElementById("Search_Wrap").style.display = "block";
    jsSwitchType("Activity");
}
function jsCloseSearchPanel(){
    document.getElementById("Search_Wrap").style.display = "none";
}
function jsSwitchType(strType){
    document.getElementById("Type_Activity").className = "type";
    document.getElementById("Search_Activity").style.display = "none";
    document.getElementById("Type_Volunteer").className = "type";
    document.getElementById("Search_Volunteer").style.display = "none";
    document.getElementById("Type_Group").className = "type"; 
    document.getElementById("Search_Group").style.display = "none";     
    switch (strType)
    { 
        case "Activity":
            document.getElementById("Type_Activity").className = "selected";
            document.getElementById("Search_Activity").style.display = "block";
            break;
        case "Volunteer":
            document.getElementById("Type_Volunteer").className = "selected";
            document.getElementById("Search_Volunteer").style.display = "block";
            break;
        case "Group":
            document.getElementById("Type_Group").className = "selected"; 
        document.getElementById("Search_Group").style.display = "block";   
            break;
    } 
}