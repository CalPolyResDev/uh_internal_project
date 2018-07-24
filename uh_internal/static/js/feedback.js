function Feedback(string, urgent){
    if(urgent == "on"){
        string = "<!channel> " + string
    }
    $.ajax({
       type:"POST",
       url:"https://hooks.slack.com/services/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",
       
       data: JSON.stringify({"text":string})
   })
}