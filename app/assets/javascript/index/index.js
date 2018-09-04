$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

    var performanceChart = echarts.init(document.getElementById('performanceChart'));
	var successChart = echarts.init(document.getElementById('successChart'));

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
	        }
	    ],
	    series : [
	    	{
	            name:'Close_True',
	            type:'bar',
	            stack: 'status',
	            itemStyle: {
				    normal: {
				       color:'#ff3333',
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
				    },
				},
	            data:[],
	        },
	        
	    ]
	};

	var lineOption = {
		title : {
	        text: '',
	    },
	    tooltip : {
	        trigger: 'axis'
	    },
	    legend: {
	        data:[],
	        left:'right',
	    },
	    xAxis : [
	        {
	            type : 'category',
	            axisLabel : {
	            	//rotate:30,
	            },
	            data : []
	        }
	    ],
	    yAxis : [
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
	            name:'Month Yields(%)',
	            type:'line',
	            smooth: true,
	            symbol:'diamond',
	            symbolSize:10,
	            data:[]
	        }
	    ]
	};

	performanceChart.setOption(barOption);
	successChart.setOption(lineOption);

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
	  			lineOption.xAxis[0].data=[];
				lineOption.series[0].data=[];
				for (let i = 0; i < data.length; i++)
				{
					if($.inArray(data[i]['month'], lineOption.xAxis[0].data) === -1) lineOption.xAxis[0].data.push(data[i]['month']);																    
				}
	  			lineOption.series[0].data = data.map(x=>x['ratio'].toFixed(2));

				successChart.setOption(lineOption);
			}

		}
	});

})