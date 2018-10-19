var timer = null;
var ready = true;

$(document).ready(function() {
  $("#timeSlider").on("input", onSliderChange);

});

function loadNew(){
  if (ready) {
	$.get("/new", function(data, status){
      if (status == "success") {
	    // send the returned student object to the populate function
        startPopulateNewSentence(data);
	  }
	});
  }
}

function startPopulateNewSentence(data){
	ready = false;
	$("#quote").fadeOut(500, function(){
            endPopulateNewSentence(data);
        });
}

function endPopulateNewSentence(data){
	$("#quote").html(data);
	$("#quote").fadeIn(500, function(){
            ready = true;
        });
}

function onSliderChange(){
	var text = "";
	var val = $("#timeSlider").val();
	if (timer != null){
		clearInterval(timer);
	}
	if (val == 0){
		text = "Manual";
	} else {
		text = "Auto: every "+val+"s";
		timer = setInterval(loadNew, val*1000);
	}
	$("#sliderlabel").html(text);

}