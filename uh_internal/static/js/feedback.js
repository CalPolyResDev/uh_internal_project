function Feedback(string, urgent){
    text_area = document.getElementById("feedback_box")
    sent_message = document.getElementById("sent_message")
    if (string == default_text){
        return;
    }
    if(urgent == true){
        string = "<!channel> " + string
        message = "Repair message sent!"
    }
    else{
        message = "Message sent!"
    }
    $.ajax({
       type:"POST",
       url:"https://hooks.slack.com/services/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",
       
       data: JSON.stringify({"text":string})
   })
   text_area.value = default_text
   sent_message.innerHTML=message
}

default_text = "Type here!"

function Focus(text_area){
    if (text_area.value == default_text){
        text_area.value = "";
    }
}

function Blur(text_area){
    if(text_area.value == "") {
        text_area.value = default_text
    }
}

window.onload = function() {
    var text_area = this.document.getElementById("feedback_box");
    text_area.value = default_text;
    text_area.onfocus = function() { Focus(this); };
    text_area.onblur = function() { Blur(this); };
}