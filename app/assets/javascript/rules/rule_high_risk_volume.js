$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

	var pathname = window.location.pathname;
	var patharr = pathname.split("/");
	var transcode = patharr[patharr.length - 1];

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
                    {name: 'ythreshold',yAxis:1000,itemStyle:{normal:{color:'#dc143c'}}},
                    {name: 'xthreshold',xAxis: 5, itemStyle:{normal:{color:'#1e90ff'}}},
                    {name: 'ythreshold2',yAxis:10000,itemStyle:{normal:{color:'#dc143c'}}},
                    {name: 'xthreshold2',xAxis: 10, itemStyle:{normal:{color:'#1e90ff'}}},

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
	            data:[],
	            markLine : {
	            	silent:true,
	                data : [
	                    {name: 'run1',yAxis:10000,itemStyle:{normal:{color:'#1e90ff'}}},
		                {name: 'run2',yAxis:100000,itemStyle:{normal:{color:'#dc143c'}}},
	                ]
	            },
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
	            data:[],
	            markLine : {
	            	silent:true,
	                data : [
	                    {name: 'run1',yAxis:5,itemStyle:{normal:{color:'#1e90ff'}}},
		                {name: 'run2',yAxis:10,itemStyle:{normal:{color:'#dc143c'}}},
	                ]
	            },
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
		  			amtlineoption.series[0].markLine.data[0].yAxis=$('#amtThreshNum').val();
		  			amtlineoption.series[0].markLine.data[1].yAxis=$('#amtThreshNum2').val();
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
		  			cntlineoption.series[0].markLine.data[0].yAxis=$('#cntThreshNum').val();
		  			cntlineoption.series[0].markLine.data[1].yAxis=$('#cntThreshNum2').val();
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

	let operateFormatter=function(value, row, index) {
	  	if(value){
			return '<a href="javascript:void(0)" class="note" >'+value+'</a>';
		}else{
			return 0;
		}
	};
	window.operateEvents = {
	  'click .note': function (e, value, row, index) {
	  	$this = $(this);

	  	$.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/prioralert',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'account_key':row.ACCOUNT_KEY}),
		  	success:function(data){

		  		tiptext = '';
		  		data.forEach(function(el) {
		  			tiptext+=el.rule_type.name+":"+el.count+"</br>"
		  		});

		  		layer.tips(tiptext, $this, {
				  tips: [3, '#3595CC'],
				  time: 3000
				});
		  	}
		  });

		    
	  }
	};

	let run2Formatter=function(value, row, index) {
		if(value==1){
			return '<span class="glyphicon glyphicon-ok" aria-hidden="true"></span>';
		}else{
			return '-';
		}
	};

	$('#alertTable').bootstrapTable({
  		pagination:true,
  		search:true,
  		exportDataType: 'all',
	    columns: [{
          field: 'state',
          checkbox: true,
          align: 'center',
          valign: 'middle'
        },{
	        field: 'ACCOUNT_KEY',
	        title: 'ACCOUNT',
	        sortable:true,
	    }, {
	        field: 'Month of Trans Date',
	        title: 'Month of Trans Date',
	        sortable:true,
	    }, {
	        field: 'TRANS_AMT',
	        title: 'Trans Amount',
	        sortable:true,
	        formatter: function formatter(value, row, index, field) {
	        	return (value).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			}
	    }, {
	        field: 'TRANS_CNT',
	        title: 'Trans Count'
	    },{
	        field: 'COUNT',
	        title: 'Prior Alerts',
	        sortable:true,
	        events: operateEvents,
	        formatter: operateFormatter
	    },{
	        field: 'run2',
	        title: 'In Both Run',
  			formatter: run2Formatter
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
		  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/alertdata/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'items':items}),
		  	success:function(data){
		  		$('#alertNum').text(items.length);
		  		$('#alertModal').modal('show'); 	  	
		  	}
		});
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
	      amtThreshNum2: {
		    digits:true,
		    min: 0,
		    greaterThan: "#threshNum"
		  },
	      cntThreshNum:{
	      	required: true,
	      	digits:true,
	      },
	      cntThreshNum2: {
		    digits:true,
		    min: 0,
		    greaterThan: "#cntThreshNum"
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

	  debugger;

	  if(!$("form").valid()){
	  	return false;
	  }

	  getHighRiskVolumeStatics($("#isOutlier").val());
	  getHighRiskVolumeAmountPercentile($("#isOutlier").val());
	  getHighRiskVolumeAmountPareto($("#isOutlier").val());
	  getHighRiskVolumeCountPercentile($("#isOutlier").val());
	  getHighRiskVolumeCountPareto($("#isOutlier").val());

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
		  	scatteroption.series[0].markLine.data[2].yAxis=$('#amtThreshNum2').val();
		  	scatteroption.series[0].markLine.data[3].xAxis=$('#cntThreshNum2').val();
		  	scatteroption.series[1].data = outlierdata;
		  	scatterChart.setOption(scatteroption);
	  	}
	  });


	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/scatterstatistics/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'crDb':$('#crDb').val(),'filename':$('#reportPath').data('keyname')
	  		,amtThreshNum:$('#amtThreshNum').val(),amtThreshNum2:$('#amtThreshNum2').val()
	  		,cntThreshNum:$('#cntThreshNum').val(),cntThreshNum2:$('#cntThreshNum2').val()}),
	  	success:function(data){
	  		console.log(data);
	  		$("#amountRun1").text(data.amount.toLocaleString('en-US', {
						  style: 'currency',
						  currency: 'USD',
						}));
	  		$("#amountRun2").text(data.amount.toLocaleString('en-US', {
						  style: 'currency',
						  currency: 'USD',
						}));
	  		$("#amountBelowRun1").text(data.below_amount_below.toLocaleString('en-US', {
						  style: 'currency',
						  currency: 'USD',
						}));
	  		$("#amountBelowRun2").text(data.below_amount_above.toLocaleString('en-US', {
						  style: 'currency',
						  currency: 'USD',
						}));
	  		$("#amountAboveRun1").text(data.above_amount_below.toLocaleString('en-US', {
						  style: 'currency',
						  currency: 'USD',
						}));
	  		$("#amountAboveRun2").text(data.above_amount_above.toLocaleString('en-US', {
						  style: 'currency',
						  currency: 'USD',
						}));
	  		$("#amountPercentRun1").text(data.percent_amount_below+'%');
	  		$("#amountPercentRun2").text(data.percent_amount_above+'%');
	  		$("#countRun1").text(data.count);
	  		$("#countRun2").text(data.count);
	  		$("#countBelowRun1").text(data.below_count_below);
	  		$("#countBelowRun2").text(data.below_count_above);	  
	  		$("#countAboveRun1").text(data.above_count_below);
	  		$("#countAboveRun2").text(data.above_count_above);
	  		$("#countPercentRun1").text(data.percent_acount_below+'%');
	  		$("#countPercentRun2").text(data.percent_acount_above+'%');	
	  	}
	  });
	  
	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/tabledata/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),crDb:$('#crDb').val()
	  		,amtThreshNum:$('#amtThreshNum').val(),cntThreshNum:$('#cntThreshNum').val()
	  		,amtThreshNum2:$('#amtThreshNum2').val(),cntThreshNum2:$('#cntThreshNum2').val()
	  	}),
	  	success:function(data){

	  		$('#alertTable').bootstrapTable('load',data);

	  	}
	  });

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/tablestatistics/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),crDb:$('#crDb').val()
	  		,amtThreshNum:$('#amtThreshNum').val(),cntThreshNum:$('#cntThreshNum').val()
	  		,amtThreshNum2:$('#amtThreshNum2').val(),cntThreshNum2:$('#cntThreshNum2').val()}),
	  	success:function(data){
	  		console.log(data);
	  		$("#run1Cust").text(data.total);
	  		$("#run2Cust").text(data.total);
	  		$("#run1CustAlerted").text(data.run1_customer);
	  		$("#run1CustAlertedPer").text(data.run1_customer_percent+'%');
	  		$("#run2CustAlerted").text(data.run2_customer);
	  		$("#run2CustAlertedPer").text(data.run2_customer_percent+'%');
	  		$("#run1CustNotAlerted").text(data.run1_customer_not);
	  		$("#run1CustNotAlertedPer").text(data.run1_customer_percent_not+'%');
	  		$("#run2CustNotAlerted").text(data.run2_customer_not);
	  		$("#run2CustNotAlertedPer").text(data.run2_customer_percent_not+'%');
	  		$("#missCust").text(data.run1_customer-data.run2_customer);

	  	}
	  });

	});

})