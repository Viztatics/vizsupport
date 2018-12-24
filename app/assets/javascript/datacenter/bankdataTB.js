$(function(){

	$('#start_date').datepicker({
		format:'yyyymmdd'
    });

    $('#end_date').datepicker({
    	format:'yyyymmdd'
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
	  'click .coltsource': function (e, value, row, index) {
	  	window.open($SCRIPT_ROOT+'/datacenter/bankdata/download/'+row.source_id,"_self");

	  }
	};

	let sourcevalidateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="btn btn-primary btn-sm sourcevalid" title="Source Validate">Validate</a>';
	};

	window.sourcevalidateEvents = {
	  'click .sourcevalid': function (e, value, row, index) {

	  	//window.open($SCRIPT_ROOT+'/datacenter/bankdata/download/'+row.id,"_self");

	  }
	};

	let alertvalidateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="btn btn-primary btn-sm alertvalid disabled" title="Alert Validate">Validate</a>';
	};

	window.alertvalidateEvents = {
	  'click .alertvalid': function (e, value, row, index) {

	  	//window.open($SCRIPT_ROOT+'/datacenter/bankdata/download/'+row.id,"_self");

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
	        title: 'Target File',
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
	        field: 'source_valid',
	        title: 'Source Valid Status',
	    },  {
            field: 'id',
            title: 'Source Validation',
            align: 'center',
            events: sourcevalidateEvents,
            formatter: sourcevalidateFormatter
        }, {
	        field: 'alert_valid',
	        title: 'Alert Valid Status',
	    },  {
            field: 'id',
            title: 'Alert Validation',
            align: 'center',
            events: alertvalidateEvents,
            formatter: alertvalidateFormatter
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
		
		$.ajax({
		  	url: $SCRIPT_ROOT+'/datacenter/bankdata/uploadhis',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'start_date':$('#start_date').val(),'end_date':$('#end_date').val()
		  			,'targetid':$('#targetFile').data('targetid'),'sourceid':$('#oneFile').data('sourceid')}),
		  	success:function(data){	
		  		$upTable.bootstrapTable('refresh');	
		  	}
		});

	});

})