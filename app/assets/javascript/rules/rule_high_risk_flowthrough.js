$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
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
                data: [
                	[
				        {
				            name: 'lower',
				            coord: [100, 111],
				            itemStyle:{normal:{color:'green'}}
				        },
				        {
				            coord: [1000000, 900000]
				        }
				    ],
	                [
				        {
				            name: 'upper',
				            coord: [100, 110],
				            itemStyle:{normal:{color:'green'}}
				        },
				        {
				            coord: [1000000, 1100000]
				        }
				    ],
				    {name: 'run1',yAxis:10000,itemStyle:{normal:{color:'#1e90ff'}}},
	                {name: 'run2',yAxis:100000,itemStyle:{normal:{color:'#dc143c'}}},					    
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
		  	url: $SCRIPT_ROOT+'/rules/flowthrough/alertdata',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'items':items}),
		  	success:function(data){	  	
		  		$('#alertNum').text(items.length);
		  		$('#alertModal').modal('show'); 
		  	}
		  });
	});

	$("#highRiskCtyForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      amtThreshNum:{
	      	required: true,
	      	digits:true,
	      	min:0,
	      },
	      amtThreshNum2: {
		    digits:true,
		    min: 0,
		    greaterThan: "#amtThreshNum"
		  },
		  lowerRatio:{
	      	required: true,
	      	digits:true,
	      	min:0,
	      },
	      upperRatio: {
		    digits:true,
		    min: 0,
		    greaterThan: "#lowerRatio"
		  },
	    },
	});

	$( "form" ).submit(function( event ) {
	  event.preventDefault();

	  if(!$("form").valid()){
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
		  	scatteroption.series[0].markLine.data[2].yAxis=$('#amtThreshNum').val();
		  	scatteroption.series[0].markLine.data[3].yAxis=$('#amtThreshNum2').val();
		  	scatterChart.setOption(scatteroption);
	  	}
	  });

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/rules/flowthrough/scatterstatistics',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({filename:$('#reportPath').data('keyname'),amtThreshNum:$('#amtThreshNum').val(),amtThreshNum2:$('#amtThreshNum2').val()}),
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
	  	url: $SCRIPT_ROOT+'/rules/flowthrough/tabledata',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),
	  		'amtThreshNum':$('#amtThreshNum').val(),
	  		'amtThreshNum2':$('#amtThreshNum2').val(),
	  		'lowerRatio':$('#lowerRatio').val(),
	  		'upperRatio':$('#upperRatio').val(),
	  	}),
	  	success:function(data){

	  		$('#alertTable').bootstrapTable('load',data);

	  	}
	  });

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/rules/flowthrough/tablestatistics',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'filename':$('#reportPath').data('keyname'),
	  		'amtThreshNum':$('#amtThreshNum').val(),'amtThreshNum2':$('#amtThreshNum2').val(),
	  		'lowerRatio':$('#lowerRatio').val(),
	  		'upperRatio':$('#upperRatio').val()}),
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