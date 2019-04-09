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
	var percentileCountChart = echarts.init(document.getElementById('percentileCountChart'));
	var run1CntChart = echarts.init(document.getElementById('run1CntChart'));
	var run1AmtChart = echarts.init(document.getElementById('run1AmtChart'));
	var run2CntChart = echarts.init(document.getElementById('run2CntChart'));
	var run2AmtChart = echarts.init(document.getElementById('run2AmtChart'));

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
	                    {name: 'Current Model',yAxis:10000,itemStyle:{normal:{color:'#1e90ff'}}},
		                {name: 'Proposed Model',yAxis:100000,itemStyle:{normal:{color:'#dc143c'}}},
	                ]
	            },
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
	                    {name: 'Current Model',yAxis:5,itemStyle:{normal:{color:'#1e90ff'}}},
		                {name: 'Proposed Model',yAxis:10,itemStyle:{normal:{color:'#dc143c'}}},
	                ]
	            },
	        }
	    ]
	};

	var	baroption = {
	    title : {
	        text: '',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data:['Alert','Non Alert']
	    },
	    xAxis : [
	        {	        	
	            type : 'category',
	            data : []
	        }
	    ],
	    yAxis : [
	        {
	        	name : 'Trans Amt',
	            type : 'value',
	            axisLabel : {
	                formatter: function(params){
	                	return "$"+params/1000+"K"

	                }
	            },
	        }
	    ],
	    series : [
	        {
	            name:'Alert',
	            type:'bar',
	            stack: '1',
	            data:[],
	        },
	        {
	            name:'Non Alert',
	            type:'bar',
	            stack: '1',
	            data:[],
	        }
	    ]
	};

	let pieOption = {
	    title : {
	        text: '',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'item',
	        formatter: "{a} <br/>{b} : {c} ({d}%)"
	    },
	    //color:['#4d94ff','#ffff66','#7b68ee','#00fa9a'],
	    series : [
	        {
	            name: '',
	            type: 'pie',
	            radius : ['50%','70%'],
	            center: ['40%', '50%'],
	            data: [],
	            label:{
	            	normal:{
	            		show:false,
	            		position:'center',
	            	},
	            	emphasis:{
	            		show:false,
	            		textStyle:{
	            			fontWeight:'bold',
	            		}
	            	}
	            },
	            labelLine:{
	            	normal:{
	            		show:false
	            	}
	            }
	        }
	    ]
	};

	let roseOption = {
	    
	    tooltip : {
	        trigger: 'item',
	        formatter: "{a} <br/>{b} : {c} ({d}%)"
	    },
	    legend: {
	        x : 'center',
	        y : 'bottom',
	        data:[],
	        show:false,
	    },
	    series : [
	        {
	            name:'Missing Cusomter From Current Model',
	            type:'pie',
	            radius : [20, 110],
	            roseType : 'area',
	            x: '50%',               // for funnel
	            max: 40,                // for funnel
	            sort : 'ascending',     // for funnel
	            data:[]
	        }
	    ]
	};
                    
                    

	scatterChart.setOption(scatteroption);
	percentileAmountChart.setOption(amtlineoption);
	percentileCountChart.setOption(cntlineoption);
	run1CntChart.setOption(pieOption);
	run1AmtChart.setOption(pieOption);
	run2CntChart.setOption(pieOption);
	run2AmtChart.setOption(pieOption);
	
	scatterChart.on('click', function(data){
		console.log(data);
		$('#clickAccount').val(data.data[2]);
		$('#scatterModal').modal('show'); 
		
	});

	$('#scatterModal').on('shown.bs.modal', function (e) {
		var profilingChart = echarts.init(document.getElementById('profilingChart'));
		$.ajax({
		  	url: $SCRIPT_ROOT+'/rules/profiling/ruledata/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),'ACCOUNT_KEY':$('#clickAccount').val()
		  			,'amtThreshNum':$('#amtThreshNum').val(),'cntThreshNum':$('#cntThreshNum').val(),'minSD':$('#minSD').val()}),
		  	success:function(data){

		  		var normaldata = [];
		  		var alertdata = [];
		  		var xAxisdata = [];
		  		$.each(data,function(index, el) {
		  			if(el['alert']==true&&index>6){
		  				alertdata.push([el['YearMonth'].toString(),el['TRANS_AMT']]);
		  			}else{
		  				normaldata.push([el['YearMonth'].toString(),el['TRANS_AMT']]);
		  			}
		  			xAxisdata.push(el['YearMonth']);	
		  			baroption.title.text = el['ACCOUNT_KEY']	  			
		  		});
		  		baroption.xAxis[0].data = xAxisdata;		  		
			  	baroption.series[0].data = alertdata;
			  	baroption.series[1].data = normaldata;
			  	profilingChart.setOption(baroption);

		  	}
		});
	    profilingChart.setOption(baroption);
	})

	var getprofilingStatics=function(includeOutlier){

		$.ajax({
		  	url: $SCRIPT_ROOT+'/rules/profiling/statisticsdata/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'filename':$('#reportPath').data('keyname')}),
		  	success:function(data){

		  		$('#statisticsTable').bootstrapTable('load',data);
		  	}
		});

	};

	var getprofilingAmountPercentile=function(includeOutlier){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/rules/profiling/percentiledata/amt/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'filename':$('#reportPath').data('keyname')}),
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

	var getprofilingCountPercentile=function(includeOutlier){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/rules/profiling/percentiledata/cnt/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'outlier':includeOutlier,'filename':$('#reportPath').data('keyname')}),
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

	$('#statisticsTable').bootstrapTable({
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
	    }, {
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
        }, {
	        field: 'ACCOUNT_KEY',
	        title: 'ACCOUNT',
	        sortable:true,
	    }, {
	        field: 'YearMonth',
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
    	console.log(ids);
	    $('#alertTable').bootstrapTable('remove', {
	      field: 'ID',
	      values: ids
	    });
	    $('#crtAlertBtn').prop('disabled', true);

	    $.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/rules/profiling/alertdata/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'items':items,'dataId':$('#dataId').val()
		  						  ,amtThreshNum:$('#amtThreshNum').val(),amtThreshNum2:$('#amtThreshNum2').val()
	  							  ,cntThreshNum:$('#cntThreshNum').val(),cntThreshNum2:$('#cntThreshNum2').val()
		  						  ,'circleName':$('#circleName').val(),'runName':$('#runName').val()}),
		  	success:function(data){	  	
		  		$('#alertNum').text(items.length);
		  		$('#alertModal').modal('show'); 
		  	}
		  });
	});

	let getScatterPlot=function(){
	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/profiling/scatterplot/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({
	  		'filename':$('#reportPath').data('keyname')
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
	};

	var getScatterStatistics=function(){

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/rules/profiling/scatterstatistics/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname')
	  		,amtThreshNum:$('#amtThreshNum').val(),amtThreshNum2:$('#amtThreshNum2').val()
	  		,cntThreshNum:$('#cntThreshNum').val(),cntThreshNum2:$('#cntThreshNum2').val()}),
	  	success:function(data){
	  		console.log(data);
	  		let run1CntOption = $.extend(true,{},pieOption)
	  		run1CntOption.title.text='Current Model Count';
	  		run1CntOption.series[0].name = 'Current Model Count';
	  		run1CntOption.series[0].data = [{value:data.below_count_below,name:"Below Threshold"},{value:data.above_count_below,name:'Above Threshold'}];
	  		run1CntChart.setOption(run1CntOption);

	  		let run1AmtOption = $.extend(true,{},pieOption)
	  		run1AmtOption.title.text='Current Model Amount';
	  		run1AmtOption.tooltip.formatter=function(params){
	  											let num = params.data.value.toLocaleString('en-US', {
																			  style: 'currency',
																			  currency: 'USD',
																			});
	  											return params.seriesName+"<br/>"+params.data.name+" : "+num+" ("+params.percent+"%)";
	  										};
	  		run1AmtOption.series[0].name = 'Current Model Amount';
	  		run1AmtOption.series[0].data = [{value:data.below_amount_below,name:"Below Threshold"},{value:data.above_amount_below,name:'Above Threshold'}];
	  		run1AmtChart.setOption(run1AmtOption);

	  		let run2CntOption = $.extend(true,{},pieOption)
	  		run2CntOption.title.text='Proposed Model Count';
	  		run2CntOption.series[0].name = 'Proposed Model Count';
	  		run2CntOption.series[0].data = [{value:data.below_count_above,name:"Below Threshold"},{value:data.above_count_above,name:'Above Threshold'}];
	  		run2CntChart.setOption(run2CntOption);

	  		let run2AmtOption = $.extend(true,{},pieOption)
	  		run2AmtOption.title.text='Proposed Model Amount';
	  		run2AmtOption.tooltip.formatter=function(params){
									let num = params.data.value.toLocaleString('en-US', {
															  style: 'currency',
															  currency: 'USD',
															});
									return params.seriesName+"<br/>"+params.data.name+" : "+num+" ("+params.percent+"%)";
								};
	  		run2AmtOption.series[0].name = 'Proposed Model Amount';
	  		run2AmtOption.series[0].data = [{value:data.below_amount_above,name:"Below Threshold"},{value:data.above_amount_above,name:'Above Threshold'}];
	  		run2AmtChart.setOption(run2AmtOption);
	  	}
	  });

	};

	let getTableData = function(){

	  $.ajax({
	  	url: $SCRIPT_ROOT+'/rules/profiling/tabledata/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname')
	  		,'amtThreshNum':$('#amtThreshNum').val(),'cntThreshNum':$('#cntThreshNum').val()
	  		,'amtThreshNum2':$('#amtThreshNum2').val(),'cntThreshNum2':$('#cntThreshNum2').val()
	  	}),
	  	success:function(data){

	  		$('#alertTable').bootstrapTable('load',data);

	  	}
	  });

	};

	let getTableStatistics = function(){

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/rules/profiling/tablestatistics/'+transcode,
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({filename:$('#reportPath').data('keyname')
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


	};

	getprofilingStatics(1);
	getprofilingAmountPercentile(1);
	getprofilingCountPercentile(1);
	getScatterPlot();
	getScatterStatistics();
	getTableData();
	getTableStatistics();

	$("#highRiskCtyForm").validate({
		ignore:"input[type=file]",
	    rules: {	    	
	      dataId: {
		    required: true,
		    digits:true,
	      	min:1,
		  },
	      amtThreshNum:{
	      	required: true,
	      	digits:true,
	      },
	      amtThreshNum2: {
		    digits:true,
		    min: 0,
		    greaterThan: "#amtThreshNum"
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
		  circleName: {
		    required: true,
		  },
		  runName: {
		    required: true,
		  },
	    },
	});

	$("#isOutlier").on('change', function(event) {
		event.preventDefault();
		/* Act on the event */
		getprofilingStatics($(this).val());		
		getprofilingAmountPercentile($(this).val());
		getprofilingCountPercentile($(this).val());


	});

	$("#missCust").on('click', function(event) {
		event.preventDefault();

		$.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/rules/profiling/runDiff/'+transcode,
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'filename':$('#reportPath').data('keyname')
	  		,amtThreshNum:$('#amtThreshNum').val(),cntThreshNum:$('#cntThreshNum').val()
	  		,amtThreshNum2:$('#amtThreshNum2').val(),cntThreshNum2:$('#cntThreshNum2').val()}),
		  	success:function(data){
		  		console.log(data);
		  		$('#missingTabs a:first').tab('show');
		  		$('#missingModal').modal('show'); 
		  		$('#missChart').height(400);
		  		$('#missChart').width(600);
		  		var missChart = echarts.init(document.getElementById('missChart'));		
		  		roseOption.series[0].data = [];  
		  		data.forEach(function (missingdata){	
					roseOption.series[0].data.push({'value':missingdata['size'],'name':missingdata['ACCOUNT_KEY']});

		  		})
		  		missChart.setOption(roseOption);
		  		$('#missingTable').bootstrapTable('load',data);

		  	}
		});
		
		/* Act on the event */
	});

	$('#missingTable').bootstrapTable({
  		pagination:true,
  		exportDataType: 'all',
  		search:true,  			
	    columns: [{
	        field: 'ACCOUNT_KEY',
	        title: 'ACCOUNT',
	    }, {
	        field: 'size',
	        title: 'Count of Transanctions',
	    }],
	});

	$( "form" ).submit(function( event ) {
	  event.preventDefault();

	  if(!$("form").valid()){
	  	return false;
	  }

	  getprofilingStatics($("#isOutlier").val());
	  getprofilingAmountPercentile($("#isOutlier").val());
	  getprofilingCountPercentile($("#isOutlier").val());
  	  getScatterPlot();
	  getScatterStatistics();
	  getTableData();
	  getTableStatistics();


	});

})