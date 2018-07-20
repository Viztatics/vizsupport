$(function(){

	var pathname = window.location.pathname;
	var patharr = pathname.split("/");
	var transcode = patharr[patharr.length - 1];

	var getHighRiskVolumeStatics=function(includeOutlier){

		$.ajax({
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/statisticsdata/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

		  		$('#statisticsAmountTable').bootstrapTable('load',data);

		  	}
		});

	};

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
	        data: ['Normal', 'Outlier']
	    },
	    tooltip : {
	        padding: 10,
	        backgroundColor: '#222',
	        borderColor: '#777',
	        borderWidth: 1,
		    formatter : function (params) {
	            return "Account Key: "+params.data[2]+"<br/>"
		                          +"Trans Month:  "+params.data[3]+"<br/>"
		                          +"Trans Count: "+params.data[0]+"<br/>"
		                          +"Trans Amt: "+(params.data[1]).toLocaleString('en-US', {
															  style: 'currency',
															  currency: 'USD',
															});
		    },
        },
	    xAxis: {
	    	name:'Trans Count',
	        splitLine: {
	            lineStyle: {
	                type: 'dashed'
	            }
	        }
	    },
	    yAxis: {
	    	name:'Trans Amt',
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
            min:1000
	    },
	    series: [{
	        name: 'Normal',
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
                data : [
                    {name: 'ythreshold',yAxis:100000,itemStyle:{normal:{color:'#dc143c'}}},
                    {name: 'xthreshold',xAxis: 5, itemStyle:{normal:{color:'#1e90ff'}}},
                ]
            },
	    },{
	        name: 'Outlier',
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

	$('#statisticsAmountTable').bootstrapTable({
  		pagination:false,
	    columns: [{
	        field: 'amt_min_data',
	        title: 'MIN',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			},
	    }, {
	        field: 'amt_max_data',
	        title: 'MAX',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }, {
	        field: 'amt_median_data',
	        title: 'MEDIAN',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }, {
	        field: 'amt_mean_data',
	        title: 'MEAN',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }],
	});

	$('#alertTable').bootstrapTable({
  		pagination:true,
  		exportDataType: 'all',
	    columns: [{
	        field: 'ACCOUNT_KEY',
	        title: 'ACCOUNT'
	    }, {
	        field: 'Month of Trans Date',
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
	    }, {
	        field: 'TRANS_CNT',
	        title: 'Trans Count'
	    }],
	});

	getHighRiskVolumeStatics(1);

	var upfile = $("#reportPath").uploadFile({
		url: $SCRIPT_ROOT+'/rules/highRiskVolume/upload',
	    maxFileCount: 1,                		   
	    allowedTypes: 'csv',  				       
	    showFileSize: false,
	    showDone: false,                           
	    showDelete: true,                          
	    showDownload:false,
	    onLoad: function(obj)
	    {    	   
	    },
	    deleteCallback: function(data,pd)
	    {

	        $.ajax({
	            cache: false,
	            url: $SCRIPT_ROOT+'/rules/highRiskVolume/upload',
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

	$('#reportPath').data('keyname')&upfile.createProgress($('#reportPath').data('keyname'));

	$("#highRiskCtyForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      threshNum:{
	      	required: true,
	      	digits:true,
	      }
	    },
	});

	$("#crDb").on('change', function(event) {
		event.preventDefault();
		/* Act on the event */
		getHighRiskVolumeStatics($("#isOutlier").val());

	});

	$("#isOutlier").on('change', function(event) {
		event.preventDefault();
		/* Act on the event */
		getHighRiskVolumeStatics($(this).val());

	});

	$( "form" ).submit(function( event ) {
	  event.preventDefault();

	  getHighRiskVolumeStatics($("#isOutlier").val());

	  filecount = $(".ajax-file-upload-container").find(".ajax-file-upload-filename").length;
	  if( filecount ==0  || !$("#highRiskCtyForm").valid()){
	  	if(filecount ==0){
	  		$("#file-error").remove();
	  		$("<label id='file-error' style='color:red;margin-left:10px'>This field is required!</label>").appendTo($('#reportPath'));
	  	}	  	
	  	return false;
	  }

	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/scatterplot',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({
	  		transCodeType:$('#transCodeType').val(),crDb:$('#crDb').val()
	  	}),
	  	success:function(data){
	  		var normaldata = [];
	  		var outlierdata = [];
	  		data.data.map(x => x[4]==1?outlierdata.push(x):normaldata.push(x));
		  	scatteroption.series[0].data = normaldata;
		  	scatteroption.series[0].markLine.data[0].yAxis=$('#amtThreshNum').val();
		  	scatteroption.series[0].markLine.data[1].xAxis=$('#cntThreshNum').val();
		  	scatteroption.series[1].data = outlierdata;
		  	scatterChart.setOption(scatteroption);
	  	}
	  });
	  
	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/tabledata',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({reportPath:$('#reportPath').val()
	  		,transCodeType:$('#transCodeType').val(),crDb:$('#crDb').val()
	  		,amtThreshNum:$('#amtThreshNum').val(),cntThreshNum:$('#cntThreshNum').val()
	  	}),
	  	success:function(data){

	  		$('#alertTable').bootstrapTable('load',data);

	  	}
	  });

	});

})