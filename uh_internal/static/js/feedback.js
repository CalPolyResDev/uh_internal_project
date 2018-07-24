function Feedback(string, urgent){
    textarea = document.getElementById("feedback_box")
    sent_message = document.getElementById("sent_message")
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
   textarea.value = default_text
   sent_message.innerHTML=message
}

default_text = "Type here!"

function Focus(textarea){
    if (textarea.value == default_text){
        textarea.value = "";
    }
}

function Blur(textarea){
    if(textarea.value == "") {
        textarea.value = default_text
    }
}

window.onload = function() {
    var textarea = this.document.getElementById("feedback_box");
    textarea.value = default_text;
    textarea.onfocus = function() { Focus(this); };
    textarea.onblur = function() { Blur(this); };
}