$(function(){

	console.log($("#datarange").val());
	var oneFile = $("#oneFile").uploadFile({
		url: $SCRIPT_ROOT+'/datacenter/bankdata/tb/upload',
		dynamicFormData:function(){
			
			return {"datalife": $("#datalife").val(),"datarange":$("#datarange").val()};
		},
	    maxFileCount: 1,
	    maxFileCount: 1, 
	    maxFileSize:20*1024*1024,                		   
	    allowedTypes: 'xlsx',  				       
	    showFileSize: false,
	    showDone: false,                           
	    showDelete: false,                          
	    showDownload:false,
	    statusBarWidth:590,
	    onSubmit: function (files) {
		    // The example input, doesn't have to be part of the upload form:
		    if (!$("#datarange").val()) {
		      $("#datarange").focus();
		      $("#file-error")&&$("#file-error").remove();
		      return false;
	    	}		    
	    },
	    onLoad: function(obj)
	    {	
	    	//if (typeof obj.createProgress !== "undefined") { 
			    //obj.createProgress($('#reportPath').data('keyname'));
			//}
	    	//     	
	    },
	    onSuccess: function(files,data,xhr,pd){
	    	//$('#reportPath').data('keyname', files[0]);
	    	$("#file-error")&&$("#file-error").remove();
	    },
	    onError: function(files,status,errMsg,pd)
		{
			console.log(errMsg);
		    //files: list of files
		    //status: error status
		    //errMsg: error message
		}
	});

	let operateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="dlcol" title="Download">Download</a>';
	};

	window.operateEvents = {
	  'click .dlcol': function (e, value, row, index) {

	  	console.log(row);
	  	window.open($SCRIPT_ROOT+'/datacenter/bankdata/download/'+row.id,"_self");

	  }
	};

	$('#uploadTable').bootstrapTable({
		idField: 'id',
		url: $SCRIPT_ROOT+'/datacenter/bankdata/uploadhis',
  		pagination:true,
  		columns: [{
	        field: 'id',
	        title: 'ID',
	    }, {
	        field: 'file_name',
	        title: 'File Name',
	    }, {
	        field: 'datalife',
	        title: 'Life circle',
	        formatter: function formatter(value, row, index, field) {
	        	if (value=='M'){
	        		return 'Month';
	        	}else if(value=='D'){
	        		return 'Day';
	        	}
			},
	    }, {
	        field: 'datarange',
	        title: 'Data Range',
	    }, {
	        field: 'username',
	        title: 'Upload User',
	    }, {
	        field: 'created_on',
	        title: 'Upload Time',
	    }, {
            field: 'file_path',
            title: 'Item Operate',
            align: 'center',
            events: operateEvents,
            formatter: operateFormatter
        },],
	});

})