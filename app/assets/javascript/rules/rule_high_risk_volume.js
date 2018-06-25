$(function(){

	
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
	    tooltip : {
	        padding: 10,
	        backgroundColor: '#222',
	        borderColor: '#777',
	        borderWidth: 1,
		    formatter : function (params) {
	            return "Account Key: "+params.data[2]+"<br/>"
		                          +"Trans Month:  "+params.data[3]+"<br/>"
		                          +"Trans Count: "+params.data[0]+"<br/>"
		                          +"Trans Amt: "+params.data[1];
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
	        name: 'Transanction',
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
                    {name: 'hello',yAxis:100000,itemStyle:{normal:{color:'#dc143c'}}},
                ]
            },
	    }]
	};

	scatterChart.setOption(scatteroption);

	$("#reportPath").uploadFile({
		url: $SCRIPT_ROOT+'/rules/highRiskVolume/upload',
	    maxFileCount: 1,                		   
	    allowedTypes: 'csv',  				       
	    showFileSize: false,
	    showDone: false,                           
	    showDelete: true,                          
	    showDownload:false,
	    onSuccess: function(files,data,xhr,pd){
	    	$("#file-error")&&$("#file-error").remove();
	    }
	});

	$("#highRiskCtyForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      threshNum:{
	      	required: true,
	      	digits:true,
	      }
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
	  	url: $SCRIPT_ROOT+'/rules/highRiskVolume/scatterplot',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({
	  		transCodeType:$('#transCodeType').val(),crDb:$('#crDb').val()
	  	}),
	  	success:function(data){
		  	scatteroption.series[0].data = data.data;
		  	scatteroption.series[0].markLine.data[0].yAxis=$('#amtThreshNum').val();
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
		  	$('#alertTable').bootstrapTable({
		  		data:data,
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
			        title: 'Trans Amount'
			    }],
			});
	  	}
	  });


	});

})