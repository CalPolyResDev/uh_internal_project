function CreateEvent(day, month, year, time, description){

}

function UpdateDays(month){
    console.log(month)
    day_list = document.getElementById("Day")

    if(day_list.length == 31 && (month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)) {
        return
    }

    if(day_list.length == 30 && (month == 4 || month == 6 || month == 9 || month == 11)){
        return
    }

    if(day_list.length == 28 && month == 2){
        return
    }

    if(month == 2){
        for (var i = day_list.length; i > 28; i--){
            day_list.remove(i-1)
        }
        return
    }

    if((month == 1 || month == 3 || month == 5 || month == 7 || month == 8 || month == 10 || month == 12)){
        for (var i = day_list.length+1; i <= 31; i++){
            option = document.createElement("OPTION")
            option.label = i.toString()
            option.value = i
            day_list.add(option, i-1)
        }
        return
    }

    if((month == 4 || month == 6 || month == 9 || month == 11) && day_list.length > 30){
        day_list.remove(30)
        return
    }
    else{
        option = document.createElement("OPTION")
        option.label = "29"
        option.value = 29
        day_list.add(option, 28)
        option2 = document.createElement("OPTION")
        option2.label = "30"
        option2.value = 30
        day_list.add(option2, 29)
    }
} 

window.onload = function() {
    UpdateDays(this.document.getElementById("Month").selectedIndex+1)
}