$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

    var initCustomer = function(){

	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/home/alert/initCusts',
		  	type: 'GET',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){
		  	}
		})

	};

    var performanceChart = echarts.init(document.getElementById('performanceChart'));
	var cusChart = echarts.init(document.getElementById('cusChart'));
	var tranChart = echarts.init(document.getElementById('tranChart'));

	var	barOption = {
	    title : {
	        text: '',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data:[]
	    },
	    xAxis : [
	        {	        	
	            type : 'category',
	            data : []
	        }
	    ],
	    yAxis : [
	        {
	        	name : 'Alert Cnt',
	            type : 'value',
	        },
	        {
	            type : 'value',
	            name : 'Percentage',
	            axisLabel : {
	                formatter: '{value} %'
	            }
	        },
	    ],
	    series : [
	    	{
	            name:'Close_True',
	            type:'bar',
	            stack: 'status',
	            itemStyle: {
				    normal: {
				       color:'#ff3333',
				       label:{
				       	show:true,
				       	color:'black',
				       },
				    },
				},
	            data:[],
	        },
	        {
	            name:'Close_False',
	            type:'bar',
	            stack: 'status',
	            itemStyle: {
				    normal: {
				       color:'#4d94ff',
				       label:{
				       	show:true,
				       	color:'black',
				       },
				    },
				},
	            data:[],
	        },
	        {
	            name:'Open',
	            type:'bar',
	            stack: 'status',
	            itemStyle: {
				    normal: {
				       color:'#ffff66',
				       label:{
				       	show:true,
				       	color:'black',
				       },
				    },
				},
	            data:[],
	        },
	        {
	            name:'Month Yields(%)',
	            type:'line',
	            yAxisIndex: 1,
	            smooth: true,
	            symbol:'diamond',
	            symbolSize:10,
	            data:[]
	        }
	    ]
	};

	let cusPieOption = {
	    title : {
	        text: 'Alerts Customer',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'item',
	        formatter: "{a} <br/>{b} : {c} ({d}%)"
	    },
	    legend: {
	        orient: 'vertical',
	        x : 'right',
	        data: []
	    },
	    color:['#ff3333','#ffff66'],
	    series : [
	        {
	            name: 'Alerts Customer',
	            type: 'pie',
	            radius : '55%',
	            center: ['40%', '50%'],
	            data: [],
	            selectedMode:'single',
	            itemStyle: {
	            	normal:{
	            		label:{
							textStyle:{
								color:'#000',
							}
	            		},
	            	},
	                emphasis: {
	                    shadowBlur: 10,
	                    shadowOffsetX: 0,
	                    shadowColor: 'rgba(0, 0, 0, 0.5)'
	                }
	            }
	        }
	    ]
	};

	let tranPieOption = {
	    title : {
	        text: 'Alerts Activity',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'item',
	        formatter: "{a} <br/>{b} : {c} ({d}%)"
	    },
	    legend: {
	        orient: 'vertical',
	        x : 'right',
	        data: []
	    },
	    color:['#ff3333','#ffff66'],
	    series : [
	        {
	            name: 'Alerts Activity',
	            type: 'pie',
	            radius : '55%',
	            center: ['40%', '50%'],
	            data: [{'name':'Alert Activity','value':5000},{'name':"Not Alert",'value':20000}],
	            selectedMode:'single',
	            itemStyle: {
	            	normal:{
	            		label:{
							textStyle:{
								color:'#000',
							}
	            		},
	            	},
	                emphasis: {
	                    shadowBlur: 10,
	                    shadowOffsetX: 0,
	                    shadowColor: 'rgba(0, 0, 0, 0.5)'
	                }
	            }
	        }
	    ]
	};

	

	performanceChart.setOption(barOption);
	cusChart.setOption(cusPieOption);
	tranChart.setOption(tranPieOption);

	$.ajax({
		cache: false,
	  	url: $SCRIPT_ROOT+'/home/alerts/monthPerf',
	  	type: 'GET',
	  	contentType:'application/json',
	  	success:function(data){

	  		console.log(data);

	  		if(data){
				barOption.xAxis[0].data=[];
				barOption.series[0].data=[];
				for (let i = 0; i < data.length; i++)
				{
					if($.inArray(data[i]['month'], barOption.xAxis[0].data) === -1) barOption.xAxis[0].data.push(data[i]['month']);																    
				}
				for(let j=0;j<3;j++){
					for(let k=0;k<barOption.xAxis[0].data.length;k++){
						barOption.series[j].data[k]=0;
						for (let i = 0; i < data.length; i++){
							if(barOption.series[j].name == data[i]['rule_status']['name']&&barOption.xAxis[0].data[k]==data[i]['month']){
								barOption.series[j].data[k]=data[i]['count'];
							}
						}														
					}						
				}	
				performanceChart.setOption(barOption);
			}

		}
	});

	$.ajax({
		cache: false,
	  	url: $SCRIPT_ROOT+'/home/alerts/monthYields',
	  	type: 'GET',
	  	contentType:'application/json',
	  	success:function(data){

	  		console.log(data);

	  		if(data){
	  			
	  			barOption.series[3].data = data.map(x=>x['ratio'].toFixed(2));

				performanceChart.setOption(barOption);
			}

		}
	});

	let getCusChart=function(){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/home/alerts/getCusPieData',
		  	type: 'GET',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){
		  		console.log(data)
				if(data){
					cusPieOption.series[0].data=[];
					for (let i = 0; i < data.length; i++)
					{
						$.each(data[i],function(index, value) {
							cusPieOption.series[0].data.push({'name':index,'value':value});
						});
					}
					cusChart.setOption(cusPieOption);
				}				
			}
		});

	};

	//initCustomer();
	getCusChart();

})