$(function(){

	$('#start_date').datepicker({
		format:'yyyymmdd'
    });

    $('#end_date').datepicker({
    	format:'yyyymmdd'
    });

/**Venn Diagram**/
		var sets = [
                    {sets:["Accounts Run1"], figure: 100, label: "Accounts Run1", size: 100},
                    {sets:["Accounts Run2"], figure: 100, label: "Accounts Run2", size: 100},
                    {sets: ["Accounts Run1", "Accounts Run2"], figure: 90, label: "Both Runs", size: 90}
                    ];


        var chart = venn.VennDiagram()
            .width(500)
            .height(400)

          

        var div = d3.select("#accountChart").datum(sets).call(chart);
            div.selectAll("text").style("fill", "white");
            div.selectAll(".venn-circle path")
                    .style("fill-opacity", .5)
                    .style("stroke-width", 1)
                    .style("stroke-opacity", 1)
                    .style("stroke", "fff");



        var tooltip = d3.select("#accountChart").append("div")
            .attr("class", "venntooltip");


        div.selectAll("g")
		    .on("mouseover", function(d, i) {
		        // sort all the areas relative to the current item
		        venn.sortAreas(div, d);

		        // Display a tooltip with the current size
		        tooltip.transition().duration(400).style("opacity", .9);
		        tooltip.text(d.size + " in " + d.label);
		        
		        // highlight the current path
		        var selection = d3.select(this).transition("tooltip").duration(400);
		        selection.select("path")
		            .style("stroke-width", 3)
		            .style("fill-opacity", d.sets.length == 1 ? .4 : .1)
		            .style("stroke-opacity", 1);
		    })

		    .on("mousemove", function() {
		        tooltip.style("left", (d3.event.pageX - 500) + "px")
		               .style("top", (d3.event.pageY - 78) + "px");
		    })
		    
		    .on("mouseout", function(d, i) {
		        tooltip.transition().duration(400).style("opacity", 0);
		        var selection = d3.select(this).transition("tooltip").duration(400);
		        selection.select("path")
		            .style("stroke-width", 0)
		            .style("fill-opacity", d.sets.length == 1 ? .5 : .0)
		            .style("stroke-opacity", 0);
		    });

                    

	let targetFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="coltarget" title="Download">'+row.target_file_name+'</a>';
	};

	window.targetEvents = {
	  'click .coltarget': function (e, value, row, index) {
	  	window.open($SCRIPT_ROOT+'/datacenter/bankdata/download/'+row.target_id,"_self");

	  }
	};

	let sourceFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="colsource" title="Download">'+row.source_file_name+'</a>';
	};

	window.sourceEvents = {
	  'click .coltsource': function(e, value, row, index) {
	  	window.open($SCRIPT_ROOT+'/datacenter/bankdata/download/'+row.source_id,"_self");

	  }
	};

	let customerStatusFormatter=function(value, row, index) {
		console.log(value);
		if(value!='-'){
			return '<a href="javascript:void(0)" class="customerstatus" title="click to show detail">'+value+'</a>';
		}else{
			return value;
		}

	};

	window.customerStatusEvents = {
	  'click .customerstatus': function(e, value, row, index) {

	  	 $('#sourceModal').modal('show'); 	 
	  }
	};

	let accountStatusFormatter=function(value, row, index) {
		console.log(value);
		if(value!='-'){
			return '<a href="javascript:void(0)" class="accountstatus" title="click to show detail">'+value+'</a>';
		}else{
			return value;
		}

	};

	window.accountStatusEvents = {
	  'click .accountstatus': function(e, value, row, index) {

	  	 $('#sourceModal').modal('show'); 	 
	  }
	};

	let transStatusFormatter=function(value, row, index) {
		console.log(value);
		if(value!='-'){
			return '<a href="javascript:void(0)" class="transstatus" title="click to show detail">'+value+'</a>';
		}else{
			return value;
		}

	};

	window.transStatusEvents = {
	  'click .transstatus': function(e, value, row, index) {

	  	 $('#sourceModal').modal('show'); 	 
	  }
	};


	let sourcevalidateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="btn btn-primary btn-sm sourcevalid" title="Source Validate">Validate</a>';
	};

	window.sourcevalidateEvents = {
	  'click .sourcevalid': function(e, value, row, index) {

	  	console.log('in');

	  	$(document).ajaxStart(function () {
	        $('#mask').addClass('lmask');	
	    });

  	 	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/datacenter/bankdata/uploadhis',
		  	type: 'PUT',
		  	contentType:'application/json',
		  	data: JSON.stringify({'his_id':row.id,'customer_valid':0,'account_valid':-1,'transaction_valid':1}),
		  	success:function(data){
		  		$upTable.bootstrapTable('refresh');	
		  		$(document).ajaxStop(function () {
			        $('#mask').removeClass('lmask');	
			    });
		  	}
		});

	  }
	};

	var $upTable = $('#uploadTable').bootstrapTable({
		idField: 'id',
		url: $SCRIPT_ROOT+'/datacenter/bankdata/uploadhis',
  		pagination:true,
  		columns: [{
	        field: 'id',
	        title: 'ID',
	    }, {
	        field: 'target_file_name',
	        title: 'AML File',
	        events: targetEvents,
            formatter: targetFormatter,
	    },{
	        field: 'source_file_name',
	        title: 'Source File',
	        events: sourceEvents,
            formatter: sourceFormatter,
	    }, {
	        field: 'start_date',
	        title: 'Start Date',
	    }, {
	        field: 'end_date',
	        title: 'End Date',
	    }, {
	        field: 'created_on',
	        title: 'Upload Time',
	    }, {
	        field: 'customer_valid',
	        title: 'Customer Valid Status',
	        align: 'center',
	        events: customerStatusEvents,
            formatter: customerStatusFormatter,
	    }, {
	        field: 'account_valid',
	        title: 'Account Valid Status',
	        align: 'center',
	        events: accountStatusEvents,
            formatter: accountStatusFormatter,
	    }, {
	        field: 'transaction_valid',
	        title: 'Transaction Valid Status',
	        align: 'center',
	        events: transStatusEvents,
            formatter: transStatusFormatter,
	    },  {
            field: 'source_id',
            title: 'Source Validation',
            align: 'center',
            events: sourcevalidateEvents,
            formatter: sourcevalidateFormatter
        }],
	});

	var targetFile = $("#targetFile").uploadFile({

		url: $SCRIPT_ROOT+'/datacenter/bankdata/tb/upload',
		//dynamicFormData:function(){			
		//	return {"start_date": $("#start_date").val(),"end_date":$("#end_date").val()};
		//},
	    maxFileCount: 1,
	    maxFileCount: 1, 
	    maxFileSize:20*1024*1024,                		   
	    //allowedTypes: 'xlsx',  				       
	    showFileSize: false,
	    showDone: false,                           
	    showDelete: false,                          
	    showDownload:false,
	    statusBarWidth:590,
	    onSubmit: function (files) {
		    // The example input, doesn't have to be part of the upload form:
		    //if (!$("#datarange").val()) {
		    //  $("#datarange").focus();
		    //  $("#file-error")&&$("#file-error").remove();
		    //  return false;
	    	//}		    
	    },
	    onLoad: function(obj)
	    {	
	    	//if (typeof obj.createProgress !== "undefined") { 
			    //obj.createProgress($('#reportPath').data('keyname'));
			//}
	    	//     	
	    },
	    onSuccess: function(files,data,xhr,pd){
	    	$('#targetFile').data('targetid', data.id);
	    	$("#file-error")&&$("#file-error").remove();
	    	//$upTable.bootstrapTable('refresh');
	    },
	    onError: function(files,status,errMsg,pd)
		{
			console.log(errMsg);
		    //files: list of files
		    //status: error status
		    //errMsg: error message
		}
		
	});

	var oneFile = $("#oneFile").uploadFile({
		url: $SCRIPT_ROOT+'/datacenter/bankdata/tb/upload',
		//dynamicFormData:function(){			
		//	return {"datalife": $("#datalife").val(),"datarange":$("#datarange").val()};
		//},
	    maxFileCount: 1,
	    maxFileCount: 1, 
	    maxFileSize:20*1024*1024,                		   
	    //allowedTypes: 'xlsx',  				       
	    showFileSize: false,
	    showDone: false,                           
	    showDelete: false,                          
	    showDownload:false,
	    statusBarWidth:590,
	    onSubmit: function (files) {
		    // The example input, doesn't have to be part of the upload form:
		    //if (!$("#datarange").val()) {
		    //  $("#datarange").focus();
		    //  $("#file-error")&&$("#file-error").remove();
		    //  return false;
	    	//}		    
	    },
	    onLoad: function(obj)
	    {	
	    	//if (typeof obj.createProgress !== "undefined") { 
			    //obj.createProgress($('#reportPath').data('keyname'));
			//}
	    	//     	
	    },
	    onSuccess: function(files,data,xhr,pd){
	    	$('#oneFile').data('sourceid', data.id);
	    	$("#file-error")&&$("#file-error").remove();
	    	//$upTable.bootstrapTable('refresh');
	    },
	    onError: function(files,status,errMsg,pd)
		{
			console.log(errMsg);
		    //files: list of files
		    //status: error status
		    //errMsg: error message
		}
	});

	$( "form" ).submit(function( event ) {
		$(document).ajaxStart(function () {
	        $('#mask').addClass('lmask');	
	    });
		$.ajax({
		  	url: $SCRIPT_ROOT+'/datacenter/bankdata/uploadhis',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'start_date':$('#start_date').val(),'end_date':$('#end_date').val()
		  			,'targetid':$('#targetFile').data('targetid'),'sourceid':$('#oneFile').data('sourceid')}),
		  	success:function(data){	
		  		$upTable.bootstrapTable('refresh');	
		  		$(document).ajaxStop(function () {
			        $('#mask').removeClass('lmask');	
			    });
		  	}
		});

	});

})