$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

    var performanceChart = echarts.init(document.getElementById('performanceChart'));
	//var successChart = echarts.init(document.getElementById('successChart'));

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

	

	performanceChart.setOption(barOption);
	//uccessChart.setOption(lineOption);

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

})