$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

	var upfile = $("#reportPath").uploadFile({
		url: $SCRIPT_ROOT+'/rules/flowthrough/upload',
	    maxFileCount: 1, 
	    maxFileSize:5*1024*1024,                		   
	    allowedTypes: 'csv',  				       
	    showFileSize: false,
	    showDone: false,                           
	    showDelete: true,                          
	    showDownload:false,
	    statusBarWidth:590,
	    onLoad: function(obj)
	    { 
	    	obj.createProgress($('#reportPath').data('keyname'));   	   
	    },
	    deleteCallback: function(data,pd)
	    {

	        $.ajax({
	            cache: false,
	            url: $SCRIPT_ROOT+'/rules/flowthrough/upload',
	            type: "DELETE",
	            dataType: "json",
	            contentType:'application/json',
	            data: JSON.stringify({keyname:$('#reportPath').data('keyname')}),
	            success: function(data) 
	            {
	            	$('#reportPath').data('keyname', "");
	                if(!data){
	                    pd.statusbar.hide();        
	                 }else{
	                    console.log(data.message); 
	                 }
	              }
	        }); 
	    },
	    onSuccess: function(files,data,xhr,pd){
	    	$('#reportPath').data('keyname', files[0]);
	    	$("#file-error")&&$("#file-error").remove();
	    }
	});

	var scatterChart = echarts.init(document.getElementById('scatterChart'));

	var scatteroption = {
	    title: {
	        text: 'Transanction Scatter Chart',	        
	        left: 'center',
	        top: 'top'
	    },	    
	    grid:{
	    	right:'15%',
	    },
	    legend: {
	        right: 10,
	        data: ['Non-Alert', 'Alert']
	    },
	    tooltip : {
	        padding: 10,
	        backgroundColor: '#222',
	        borderColor: '#777',
	        borderWidth: 1,
		    formatter : function (params) {
	            return "Account Key: "+params.data[2]+"<br/>"
		                          +"Trans Month:  "+params.data[3]+"<br/>"
		                          +"Dollar In: "+(params.data[0]|0).toLocaleString('en-US', {
															  style: 'currency',
															  currency: 'USD',
															})+"<br/>"
		                          +"Dollar out: "+(params.data[1]|0).toLocaleString('en-US', {
															  style: 'currency',
															  currency: 'USD',
															});
		    },
        },
	    xAxis: {
	    	name:'Dollar In',
	    	type: 'log',
	    	logBase:10,
	        splitLine: {
	            lineStyle: {
	                type: 'dashed'
	            }
	        },
	        axisLabel : {
                formatter: function(params){
                	return "$"+params/1000+"K"

                }
            },
            min:100
	    },
	    yAxis: {
	    	name:'Dollar Out',
	    	type: 'log',
	    	logBase:10,
	        splitLine: {
	            lineStyle: {
	                type: 'dashed'
	            }
	        },
	        axisLabel : {
                formatter: function(params){
                	return "$"+params/1000+"K"

                }
            },
            min:100
	    },
	    series: [{
	        name: 'Non-Alert',
	        data: [
            ],
	        type: 'scatter',
	        itemStyle: {
	            normal: {
	                shadowBlur: 10,
	                shadowColor: 'rgba(25, 100, 150, 0.5)',
	                shadowOffsetY: 5,
	                color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [{
	                    offset: 0,
	                    color: 'rgb(129, 227, 238)'
	                }, {
	                    offset: 1,
	                    color: 'rgb(25, 183, 207)'
	                }])
	            }
	        },	        
            markLine : {
            	silent:true,
            	lineStyle:{
            		color:'green',
            	},
                data: [
                	[
				        {
				            name: 'lower',
				            coord: [100, 111]
				        },
				        {
				            coord: [1000000, 900000]
				        }
				    ],
	                [
				        {
				            name: 'upper',
				            coord: [100, 110]
				        },
				        {
				            coord: [1000000, 1100000]
				        }
				    ],					    
				]
            },
	    },{
	        name: 'Alert',
	        data: [
            ],
	        type: 'scatter',
	        itemStyle: {
	            normal: {
	                shadowBlur: 10,
	                shadowColor: 'rgba(120, 36, 50, 0.5)',
	                shadowOffsetY: 5,
	                color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [{
	                    offset: 0,
	                    color: 'rgb(251, 118, 123)'
	                }, {
	                    offset: 1,
	                    color: 'rgb(204, 46, 72)'
	                }])
	            }
	        },	
	    }]
	};
            

	scatterChart.setOption(scatteroption);
	

	$('#alertTable').bootstrapTable({
  		pagination:true,
  		exportDataType: 'all',
	    columns: [{
          field: 'state',
          checkbox: true,
          align: 'center',
          valign: 'middle'
        }, {
	        field: 'ACCOUNT_KEY',
	        title: 'ACCOUNT'
	    }, {
	        field: 'YearMonth',
	        title: 'Month of Trans Date'
	    }, {
	        field: 'TRANS_AMT',
	        title: 'Trans Amount',
	        formatter: function formatter(value, row, index, field) {
	        	return (value).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }],
	});

	$('#alertTable').closest('.fixed-table-container').css('height', '450px');    

    $('#alertTable').on('check.bs.table uncheck.bs.table check-all.bs.table uncheck-all.bs.table', () => {
    	
	    $('#crtAlertBtn').prop('disabled', !$('#alertTable').bootstrapTable('getSelections').length);
	});

	$('#crtAlertBtn').click(() => {
		ids = $.map($('#alertTable').bootstrapTable('getSelections'), function(item, index) {
    		return item.ID;
    	});
    	items = $.map($('#alertTable').bootstrapTable('getSelections'), function(item, index) {
    		return item;
    	});
	    $('#alertTable').bootstrapTable('remove', {
	      field: 'ID',
	      values: ids
	    });
	    $('#crtAlertBtn').prop('disabled', true);

	    $.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/rules/flowthrough/alertdata',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'items':items}),
		  	success:function(data){	  	
		  	}
		  });
	});

	$("#highRiskCtyForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      amtThreshNum:{
	      	required: true,
	      	digits:true,
	      },
	    },
	});

	$( "form" ).submit(function( event ) {
	  event.preventDefault();

	  filecount = $(".ajax-file-upload-container").find(".ajax-file-upload-filename").length;
	  if( filecount ==0  || !$("#highRiskCtyForm").valid()){
	  	if(filecount ==0){
	  		$("#file-error").remove();
	  		$("<label id='file-error' style='color:red;margin-left:10px'>This field is required!</label>").appendTo($('#reportPath'));
	  	}	  	
	  	return false;
	  }

	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/flowthrough/scatterplot',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({
	  		'filename':$('#reportPath').data('keyname'),
	  		'amtThreshNum':$('#amtThreshNum').val(),
	  		'lowerRatio':$('#lowerRatio').val(),
	  		'upperRatio':$('#upperRatio').val(),
	  	}),
	  	success:function(data){
	  		var normaldata = [];
	  		var outlierdata = [];
	  		data.data.map(x => x[4]==true?outlierdata.push(x):normaldata.push(x));
		  	scatteroption.series[0].data = normaldata;
		  	scatteroption.series[1].data = outlierdata;
		  	scatteroption.series[0].markLine.data[0][0].coord = [100/$('#lowerRatio').val()*100,100]
		  	scatteroption.series[0].markLine.data[0][1].coord = [1000000,1000000*$('#lowerRatio').val()/100]
		  	scatteroption.series[0].markLine.data[1][0].coord = [100,100*$('#upperRatio').val()/100]
		  	scatteroption.series[0].markLine.data[1][1].coord = [1000000/$('#upperRatio').val()*100,1000000]
		  	scatterChart.setOption(scatteroption);
	  	}
	  });
	  
	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/flowthrough/tabledata',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),
	  		'amtThreshNum':$('#amtThreshNum').val(),
	  		'lowerRatio':$('#lowerRatio').val(),
	  		'upperRatio':$('#upperRatio').val(),
	  	}),
	  	success:function(data){

	  		$('#alertTable').bootstrapTable('load',data);

	  	}
	  });

	});

})