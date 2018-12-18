$(function(){
	$.validator.addMethod("greaterThan",
	    function (value, element, param) {
	          var $otherElement = $(param);
	          return parseInt(value, 10) > parseInt($otherElement.val(), 10);
	    }, $.validator.format( "Please enter a number greater than threshold below the line." )
	);
})