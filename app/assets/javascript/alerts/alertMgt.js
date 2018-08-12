$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

    let statusChart = echarts.init(document.getElementById('statusChart'));
	let typeChart = echarts.init(document.getElementById('typeChart'));
	let barChart = echarts.init(document.getElementById('barChart'));

	let statusOption = {
	    title : {
	        text: 'Alerts Status',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'item',
	        formatter: "{a} <br/>{b} : {c} ({d}%)"
	    },
	    legend: {
	        orient: 'vertical',
	        x : 'right',
	        data: ['Open','Close_True','Close_False']
	    },
	    series : [
	        {
	            name: 'status',
	            type: 'pie',
	            radius : '55%',
	            center: ['40%', '50%'],
	            data: [],
	            itemStyle: {
	                emphasis: {
	                    shadowBlur: 10,
	                    shadowOffsetX: 0,
	                    shadowColor: 'rgba(0, 0, 0, 0.5)'
	                }
	            }
	        }
	    ]
	};

	let typeOption = {
	    title : {
	        text: 'Alerts Rules',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'item',
	        formatter: "{a} <br/>{b} : {c} ({d}%)"
	    },
	    legend: {
	        orient: 'vertical',
        	x : 'right',
	        data: ['High_Risk_Country','High_Volume_Value','Profiling','Flow_Through']
	    },
	    series : [
	        {
	            name: 'rules',
	            type: 'pie',
	            radius : '55%',
	            center: ['40%', '50%'],
	            data: [],
	            itemStyle: {
	                emphasis: {
	                    shadowBlur: 10,
	                    shadowOffsetX: 0,
	                    shadowColor: 'rgba(0, 0, 0, 0.5)'
	                }
	            }
	        }
	    ]
	};

	let barOption = {
		title : {
	        text: 'Alerts Analysts Distribution',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'axis',
	        axisPointer : {            
	            type : 'line'        
	        }
	    },
	    legend: {
	    	orient: 'vertical',
        	x : 'right',
	        data:['Open','Close_True','Close_False']
	    },
	    xAxis : [
	        {
	        	name : 'analyst',
	            type : 'category',
	            data : []
	        }
	    ],
	    yAxis : [
	        {
	        	name : 'alerts',
	            type : 'value'
	        }
	    ],
	    series : [
	        {
	            name:'Open',
	            type:'bar',
	            stack: 'status',
	            data:[]
	        },
	        {
	            name:'Close_True',
	            type:'bar',
	            stack: 'status',
	            data:[]
	        },
	        {
	            name:'Close_False',
	            type:'bar',
	            stack: 'status',
	            data:[]
	        }
	    ]
	};

	statusChart.setOption(statusOption);
	typeChart.setOption(typeOption);

	let getStatusChart=function(){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/statuschart',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){

				if(data){
					statusOption.series[0].data=[];
					for (let i = 0; i < data.length; i++)
					{
					    statusOption.series[0].data.push({name:data[i][1],value:data[i][0]})
					}
					statusChart.setOption(statusOption);
				}				
			}
		});

	};

	let getTypeChart=function(){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/typechart',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){

				if(data){
					typeOption.series[0].data=[];
					for (let i = 0; i < data.length; i++)
					{
					    typeOption.series[0].data.push({name:data[i][1],value:data[i][0]})
					}
					typeChart.setOption(typeOption);
				}				
			}
		});

	};

	let getBarChart=function(){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/barchart',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){

				if(data){
					barOption.xAxis[0].data=[];
					barOption.series[0].data=[];
					for (let i = 0; i < data.length; i++)
					{
						if($.inArray(data[i][1], barOption.xAxis[0].data) === -1) barOption.xAxis[0].data.push(data[i][1]);
						for(let j=0;j<3;j++){
							if(barOption.series[j].name == data[i][2]){
								barOption.series[j].data.push({name:data[i][1],value:data[i][0]})
							}
						}											    
					}
					barChart.setOption(barOption);
				}			
			}
		});

	};

	let operateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="note" title="Add note">Add Note</a>';
	};

	window.operateEvents = {
	  'click .note': function (e, value, row, index) {

	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/getcurrentnote',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'alertid':row.id}),
		  	success:function(data){

		  		console.log(data);

		  		//restore to init
		  		$('#commentTextArea').prop('disabled',false);
				$('#processCtl').bootstrapToggle('enable');
				$('#processCtl').bootstrapToggle('off');
				$('#noteSaveBtn').prop('disabled',false);

		  		$('#alertProcessModal').data('alertid', data.id);
		  		$('#alertProcessModal').data('processid', data.pid);

				if(data.rule_status!=='Close_True'){
					$('#processCtl').bootstrapToggle('off');					
				}else{
					$('#processCtl').bootstrapToggle('on');					
				}

				if(data.comment){
					$('#commentTextArea').val(data.comment);
					$("#processCtl").bootstrapToggle('enable');
				}else{
					$('#commentTextArea').val('');
					$("#processCtl").bootstrapToggle('disable');
				}

				if(data.rule_status!=='Open'){
					$('#commentTextArea').prop('disabled','disabled');
					$('#processCtl').bootstrapToggle('disable');
					$('#noteSaveBtn').prop('disabled','disabled');
				}
				
						
			}
		});

	    $('#alertProcessModal').modal('show');  
	  }
	};

	var $alerttable = $('#alertTable').bootstrapTable({
		idField: 'id',
		url: $SCRIPT_ROOT+'/alerts/management/gettabledata',
  		pagination:true,
	    columns: [{
	        field: 'id',
	        title: 'Alert ID',
	    }, {
	        field: 'rule_type',
	        title: 'Rule',
	    }, {
	        field: 'account_key',
	        title: 'Account Key',
	    },{
	        field: 'trans_month',
	        title: 'Month of Trans Date',
	    }, {
	        field: 'country_abbr',
	        title: 'Opposite Country',
	    },{
	        field: 'country_name',
	        title: 'Country Name',
	    },{
	        field: 'amount',
	        title: 'Trans Amount',
	        formatter: function formatter(value, row, index, field) {
	        	return (value).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			},
	    },{
	        field: 'cnt',
	        title: 'Trans Cnt',
	    },{
	        field: 'rule_status',
	        title: 'Status',
	    },{
	        field: 'uid',
	        title: 'Assigned User',
	        editable: {
                type: 'select',
                source:$SCRIPT_ROOT+'/alerts/management/getanalystsbycompany',
                url:$SCRIPT_ROOT+'/alerts/management/assignanalyst',
                success: function(echo) {
					getBarChart();
				},
                noeditFormatter:function(value, row, index) {
			        if (row.rule_status=='Open') {
			          return false;  // return false if you want the field editable.
			        } else {
			          return row.username;
			        }
			    }
            }
	    },{
          field: 'username',
          title: 'Item Operate',
          align: 'center',
          events: operateEvents,
          formatter: operateFormatter
        }],
	});

	$('#alertTable').on('load-success.bs.table', function (data) {

		//$alerttable.bootstrapTable('hideColumn', 'username');
		if($('#alertMgt').data('ismanager')=='False'){
			$alerttable.bootstrapTable('hideColumn', 'uid');
		}

	});

	$('#commentTextArea').bind('input propertychange', function() {
	      $("#processCtl").bootstrapToggle('disable');
	      if(this.value.length){
	        $("#processCtl").bootstrapToggle('enable');
	      }
	});

	$("#alertNoteForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      commentTextArea:{
	      	required: true,
	      }
	    },
	});

	$( "form" ).submit(function( event ) {
	  event.preventDefault();

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/alerts/management/addnote',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'alert_id':$('#alertProcessModal').data('alertid'),'process_id':$('#alertProcessModal').data('processid'),
	  			'comment':$('#commentTextArea').val(),'status':$('#processCtl').prop('checked')}),
	  	success:function(data){
	  		$('#alertProcessModal').modal('hide');
	  		$alerttable.bootstrapTable('refresh');
	  		init();		  	
	  	}
	  });

	});

	let init=function(){

		if($('#alertMgt').data('ismanager')=='True'){		
			getBarChart();
		}else{
			$('#managerBar').css('display', 'none');
		}
		getStatusChart();
		getTypeChart();
		//getAlertTable();
				

	};

	init();
  

})