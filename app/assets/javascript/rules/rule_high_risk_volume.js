$(function(){

	var pathname = window.location.pathname;
	var patharr = pathname.split("/");
	var transcode = patharr[patharr.length - 1];

	var upfile = $("#reportPath").uploadFile({
		url: $SCRIPT_ROOT+'/rules/highRiskVolume/upload',
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

	var scatterChart = echarts.init(document.getElementById('scatterChart'));
	var percentileAmountChart = echarts.init(document.getElementById('percentileAmountChart'));
	var paretoAmountChart = echarts.init(document.getElementById('paretoAmountChart'));
	var percentileCountChart = echarts.init(document.getElementById('percentileCountChart'));
	var paretoCountChart = echarts.init(document.getElementById('paretoCountChart'));

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
		                          +"Trans Amt: "+(params.data[1]|0).toLocaleString('en-US', {
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
            min:100
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
            	silent:true,
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

	var amtlineoption = {
	    title : {
	        text: 'Amount Percentile Distribution(Transanction Analysis)',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    xAxis : [
	        {
	            type : 'category',
	            boundaryGap : false,
	            data : ['0%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%']
	        }
	    ],
	    yAxis : [
	        {
	            type: 'log',
	    		logBase:10,
	            axisLabel : {
	                formatter: function(params){
	                	return "$"+params/1000+"K"

	                }
	            },
	        }
	    ],
	    series : [
	        {
	            name:'',
	            type:'line',
	            smooth: true,
	            symbol:'diamond',
	            symbolSize:10,
	            data:[]
	        }
	    ]
	};

	var amtlinebaroption = {
		title : {
	        text: 'Amount Pareto Analysis(Customer Analysis)',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data:['Trans Amount','Cumulative Percentage'],
	        left:'right',
	    },
	    grid:{
	    	y2:'12%',
	    },
	    xAxis : [
	        {
	            type : 'category',
	            axisLabel : {
	            	rotate:30,
	            },
	            data : []
	        }
	    ],
	    yAxis : [
	        {
	            type : 'value',
	            axisLabel : {
	                formatter: function(params){
	                	return "$"+params/1000+"K"

	                }
	            },
	        },
	        {
	            type : 'value',
	            axisLabel : {
	                formatter: '{value} %'
	            }
	        }
	    ],
	    series : [

	        {
	            name:'Trans Amount',
	            type:'bar',
	            data:[]
	        },
	        {
	            name:'Cumulative Percentage',
	            type:'line',
	            yAxisIndex: 1,
	            symbol:'diamond',
	            symbolSize:10,
	            data:[]
	        }
	    ]
	};

	var cntlineoption = {
	    title : {
	        text: 'Count Percentile Distribution(Transanction Analysis)',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    xAxis : [
	        {
	            type : 'category',
	            boundaryGap : false,
	            data : ['0%','10%','20%','30%','40%','50%','60%','70%','80%','90%','100%']
	        }
	    ],
	    yAxis : [
	        {
	            type: 'value',
	        }
	    ],
	    series : [
	        {
	            name:'',
	            type:'line',
	            smooth: true,
	            symbol:'diamond',
	            symbolSize:10,
	            data:[]
	        }
	    ]
	};

	var cntlinebaroption = {
		title : {
	        text: 'Count Pareto Analysis(Customer Analysis)',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data:['Trans Count','Cumulative Percentage'],
	        left:'right',
	    },
	    grid:{
	    	y2:'12%',
	    },
	    xAxis : [
	        {
	            type : 'category',
	            axisLabel : {
	            	rotate:30,
	            },
	            data : []
	        }
	    ],
	    yAxis : [
	        {
	            type : 'value',
	        },
	        {
	            type : 'value',
	            axisLabel : {
	                formatter: '{value} %'
	            }
	        }
	    ],
	    series : [

	        {
	            name:'Trans Count',
	            type:'bar',
	            data:[]
	        },
	        {
	            name:'Cumulative Percentage',
	            type:'line',
	            yAxisIndex: 1,
	            symbol:'diamond',
	            symbolSize:10,
	            data:[]
	        }
	    ]
	};

	scatterChart.setOption(scatteroption);
	percentileAmountChart.setOption(amtlineoption);
	paretoAmountChart.setOption(amtlinebaroption);
	percentileCountChart.setOption(cntlineoption);
	paretoCountChart.setOption(cntlinebaroption);

	var getHighRiskVolumeStatics=function(includeOutlier){

		$.ajax({
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/statisticsdata/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

		  		$('#statisticsAmountTable').bootstrapTable('load',data);
		  		$('#statisticsCountTable').bootstrapTable('load',data);

		  	}
		});

	};

	var getHighRiskVolumeAmountPercentile=function(includeOutlier){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/percentiledata/amt/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

		  		if(data){
		  			amtlineoption.series[0].data = data.map(x=>!x?0:x.toFixed(2));
			  		percentileAmountChart.setOption(amtlineoption);
		  		}

		  	}
		});

	};

	var getHighRiskVolumeAmountPareto=function(includeOutlier){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/paretodata/amt/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

		  		if(data){
	  				amtlinebaroption.xAxis[0].data=[];
	  				amtlinebaroption.series[0].data=[];
	  				amtlinebaroption.series[1].data=[];
		  			data.forEach(function(singledata){
						amtlinebaroption.xAxis[0].data.push(singledata['ACCOUNT_KEY']);
						amtlinebaroption.series[0].data.push(singledata['TRANS_AMT'].toFixed(2));
				  		amtlinebaroption.series[1].data.push(singledata['percentage'].toFixed(2)); 
					    paretoAmountChart.setOption(amtlinebaroption);
				  	})
		  		}				
			}
		});

	};

	var getHighRiskVolumeCountPercentile=function(includeOutlier){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/percentiledata/cnt/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

		  		if(data){
		  			cntlineoption.series[0].data = data.map(x=>!x?0:x.toFixed(2));
			  	    percentileCountChart.setOption(cntlineoption);
		  		}
		  	}
		});

	};

	var getHighRiskVolumeCountPareto=function(includeOutlier){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/paretodata/cnt/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

	  			cntlinebaroption.xAxis[0].data=[];
	  			cntlinebaroption.series[0].data=[];
	  			cntlinebaroption.series[1].data=[];
				data.forEach(function(singledata){
					cntlinebaroption.xAxis[0].data.push(singledata['ACCOUNT_KEY']);
					cntlinebaroption.series[0].data.push(singledata['TRANS_CNT'].toFixed(2));
			  		cntlinebaroption.series[1].data.push(singledata['percentage'].toFixed(2)); 
				    paretoCountChart.setOption(cntlinebaroption);
			  	})
			}
		});

	};

	$('#statisticsAmountTable').bootstrapTable({
  		pagination:false,
	    columns: [{
	        field: 'amt_min_data',
	        title: 'MIN_AMOUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			},
	    }, {
	        field: 'amt_max_data',
	        title: 'MAX_AMOUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }, {
	        field: 'amt_median_data',
	        title: 'MEDIAN_AMOUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }, {
	        field: 'amt_mean_data',
	        title: 'MEAN_AMOUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return (value|0).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }],
	});

	$('#statisticsCountTable').bootstrapTable({
  		pagination:false,
	    columns: [{
	        field: 'cnt_min_data',
	        title: 'MIN_COUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return !value?0:value.toFixed(2);
			},
	    }, {
	        field: 'cnt_max_data',
	        title: 'MAX_COUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return !value?0:value.toFixed(2);
			}
	    }, {
	        field: 'cnt_median_data',
	        title: 'MEDIAN_COUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return !value?0:value.toFixed(2);
			}
	    }, {
	        field: 'cnt_mean_data',
	        title: 'MEAN_COUNT',
	        formatter: function formatter(value, row, index, field) {
	        	return !value?0:value.toFixed(2);
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
	getHighRiskVolumeAmountPercentile(1);
	getHighRiskVolumeAmountPareto(1);
	getHighRiskVolumeCountPercentile(1);
	getHighRiskVolumeCountPareto(1);

	$("#highRiskCtyForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      amtThreshNum:{
	      	required: true,
	      	digits:true,
	      },
	      cntThreshNum:{
	      	required: true,
	      	digits:true,
	      },
	    },
	});

	$("#crDb").on('change', function(event) {
		event.preventDefault();
		/* Act on the event */
		getHighRiskVolumeStatics($("#isOutlier").val());
		getHighRiskVolumeAmountPercentile($("#isOutlier").val());
		getHighRiskVolumeAmountPareto($("#isOutlier").val());
		getHighRiskVolumeCountPercentile($("#isOutlier").val());
		getHighRiskVolumeCountPareto($("#isOutlier").val());		

	});

	$("#isOutlier").on('change', function(event) {
		event.preventDefault();
		/* Act on the event */
		getHighRiskVolumeStatics($(this).val());		
		getHighRiskVolumeAmountPercentile($(this).val());
		getHighRiskVolumeAmountPareto($(this).val());
		getHighRiskVolumeCountPercentile($(this).val());
		getHighRiskVolumeCountPareto($(this).val());		


	});

	$( "form" ).submit(function( event ) {
	  event.preventDefault();

	  getHighRiskVolumeStatics($("#isOutlier").val());
	  getHighRiskVolumeAmountPercentile($("#isOutlier").val());
	  getHighRiskVolumeAmountPareto($("#isOutlier").val());
	  getHighRiskVolumeCountPercentile($("#isOutlier").val());
	  getHighRiskVolumeCountPareto($("#isOutlier").val());

	  filecount = $(".ajax-file-upload-container").find(".ajax-file-upload-filename").length;
	  if( filecount ==0  || !$("#highRiskCtyForm").valid()){
	  	if(filecount ==0){
	  		$("#file-error").remove();
	  		$("<label id='file-error' style='color:red;margin-left:10px'>This field is required!</label>").appendTo($('#reportPath'));
	  	}	  	
	  	return false;
	  }

	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/scatterplot/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({
	  		'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')
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
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/tabledata/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),crDb:$('#crDb').val()
	  		,amtThreshNum:$('#amtThreshNum').val(),cntThreshNum:$('#cntThreshNum').val()
	  	}),
	  	success:function(data){

	  		$('#alertTable').bootstrapTable('load',data);

	  	}
	  });

	});

})