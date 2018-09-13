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
	        text: 'Alerts Aging',
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
	    color:['#4d94ff','#ffff66','#7b68ee','#00fa9a'],
	    series : [
	        {
	            name: 'status',
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

	let typeOption = {
	    title : {
	        text: 'Alerts Rule Types',
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
	    color:['#ff3333','#4d94ff','#ffff66','#7b68ee'],
	    series : [
	        {
	            name: 'rules',
	            type: 'pie',
	            radius : '55%',
	            center: ['40%', '50%'],
	            data: [],
	            selectedMode:'single',	            
				textStyle:{
					color:'black',
				},
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

	statusChart.setOption(statusOption);
	typeChart.setOption(typeOption);

	let getStatusChart=function(){

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/dateagingchart',
		  	type: 'GET',
		  	contentType:'application/json',
		  	success:function(data){

		  		console.log(data);

				if(data){
					statusOption.legend.data=[];
					statusOption.series[0].data=[];
					for (let i = 0; i < data.length; i++)
					{
						statusOption.legend.data.push(data[i]['aging']);
						if(data[i]['aging']=='Due Today(30)'){
							statusOption.series[0].data.push({name:data[i]['aging'],value:data[i]['count'],itemStyle:{normal:{color:'#ff3333'}}});
						}else{
							statusOption.series[0].data.push({name:data[i]['aging'],value:data[i]['count']});
						}
					    
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
					}
					for(let j=0;j<3;j++){
						for(let k=0;k<barOption.xAxis[0].data.length;k++){
							barOption.series[j].data[k]=0;
							for (let i = 0; i < data.length; i++){
								if(barOption.series[j].name == data[i][2]&&barOption.xAxis[0].data[k]==data[i][1]){
									barOption.series[j].data[k]=data[i][0];
								}
							}														
						}						
					}	
					barChart.setOption(barOption);
				}			
			}
		});

	};

	let operateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="btn btn-primary btn-sm note" title="Add note">Add Note</a>';
	};

	window.operateEvents = {
	  'click .note': function (e, value, row, index) {

	  	$("#commentAttachment").data('aid', row.id);

	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/getcurrentnote',
		  	type: 'POST',
		  	contentType:'application/json',
		  	data: JSON.stringify({'alertid':row.id}),
		  	success:function(data){

		  		console.log(data);

		  		if($('.ajax-file-upload-container')){
		  			$('.ajax-file-upload-container').remove();
		  		}

		  		//restore to init
		  		$('#commentTextArea').prop('disabled',false);
		  		$('#commentTextArea').val('');
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

				if(data.rule_status!=='Open'){
					//$('#commentTextArea').prop('disabled','disabled');
					$('#processCtl').bootstrapToggle('disable');
					//$('#noteSaveBtn').prop('disabled','disabled');
				}

				var upfile = $("#commentAttachment").uploadFile({
					url: $SCRIPT_ROOT+'/alerts/management/upload/'+$("#commentAttachment").data('aid')+'/0',
				    maxFileCount: 1, 
				    maxFileSize:5*1024*1024,                		   
				    //allowedTypes: 'csv',  				       
				    showFileSize: false,
				    showDone: false,                           
				    showDelete: true,                          
				    showDownload:false,
				    //statusBarWidth:590,
				    onLoad: function(obj)
				    {	
				    	//if (typeof obj.createProgress !== "undefined") { 
						    //obj.createProgress($('#reportPath').data('keyname'));
						//}
				    	//     	
				    },
				    deleteCallback: function(data,pd)
				    {

				        $.ajax({
				            cache: false,
				            url: $SCRIPT_ROOT+'/alerts/management/upload/'+$("#commentAttachment").data('aid')+'/0',
				            type: "DELETE",
				            dataType: "json",
				            contentType:'application/json',
				            data: JSON.stringify({keyname:$('#commentAttachment').data('keyname')}),
				            success: function(data) 
				            {
				            	$('#commentAttachment').data('keyname', "");
				                if(!data){
				                    pd.statusbar.hide();        
				                 }
				              }
				        }); 
				    },
				    onSuccess: function(files,data,xhr,pd){
				    	console.log(files);
				    	$('#commentAttachment').data('keyname', files[0]);
				    }
				});


				
						
			}
		});

		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/procescomments/'+row.id+"/Analyst_Process",
		  	type: 'GET',
		  	data: JSON.stringify({}),
		  	success:function(comments){
	  		console.log(comments);
	  			$('#aComments').empty();
				$ele = $('.commentscls').clone();
				$ele[0].style.display = 'block';
				comments.forEach(function(row){					
					//console.log(row);
					$clonele = $ele.clone().html(function(index,html){
						return html.replace('#commentor#',row.creator).replace('#comment_on#',row.created_on)
						.replace('#comment#',row.comment);						
					});
					if(row.attachment){
						$clonele.find('.ctl-comment-attached')[0].style.display = 'block';
						$clonele.html(function(index,html){
							return html.replace('#ctl_comment_attached#',row.attachment.split("/")[4])
								.replace('#ctl_href#','https://s3.amazonaws.com/vizrules/'+row.attachment);
						});				
					}
					$('#aComments').append($clonele);					
				})
		  	}
		  });

	    $('#alertProcessModal').modal('show');  
	  }
	};

	let idFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="aid" title="click to show detail">'+value+'</a>';
	};

	window.idEvents = {
	  'click .aid': function (e, value, row, index) {
	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/alertDetail/'+value,
		  	type: 'GET',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){

		  		console.log(data);
		  		//$("#altId").text(data[0].id);	
		  		$("#altAcckey").text(data[0].account_key||'-');
		  		$("#altTransMonth").text(data[0].trans_month||'-');
		  		$("#altTransAmount").text(data[0].amount.toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				})||'-');
		  		$("#altTransCnt").text(data[0].cnt||'-');
		  		$("#altOppoCtry").text(data[0].country_abbr||'-');
		  		$("#altCtryName").text(data[0].country_name||'-');
		  		$("#altOwner").text(data[0].cuid||'-');
		  		$("#altRuleType").text(data[0].rule_type||'-');
		  		$("#altRuleStatus").text(data[0].rule_status||'-');
		  		$("#altTriRule").text(data[0].trigger_rule||'-');
		  		$("#altCurrentStep").text(data[0].current_step||'-');
		  		$("#altOperator").text(data[0].ouid||'-');
		  		$("#altOperatedDate").text(data[0].operated_on||'-');
		  		$("#altCreatedDate").text(data[0].created_on||'-');
				$("#altFinishedDate").text(data[0].finished_on||'-');
				
				$('#aProcess').empty();
				$ele = $('.procls').clone();
				$ele[0].style.display = 'block';
				data.forEach(function(row){					
					//console.log(row);
					$clonele = $ele.clone().html(function(index,html){
						return html.replace('#process_type#',row.process_type).replace('#assigner#',row.assigner)
						.replace('#assigned_on#',row.assigned_on).replace('#syslog#',row.syslog).replace(/#pid#/gi,row.pid);
					});
					if(row.process_type==='Alert_Created'){
						$clonele.find('a').remove();
						$clonele.find('.collapse').remove();
					}
					$('#aProcess').append($clonele);					
				})

				$('.collapse').on('show.bs.collapse', function () {
				  $this = $(this);
				  var idstr =  $this.prop('id');
				  var pid = idstr.split("_")[1];

				  $.ajax({
					cache: false,
				  	url: $SCRIPT_ROOT+'/alerts/management/procescomments/'+pid,
				  	type: 'GET',
				  	contentType:'application/json',
				  	data: JSON.stringify({}),
				  	success:function(data){
				  	  $this.empty();
					  $ele = $('.well[style="margin-bottom:0;display: none"]').clone();
					  $ele[0].style.display = 'block';
					  if(data.length === 0){
					  	$clonele = $ele.clone().empty().append('No comments!');
					  	$this.append($clonele);
					  }else{
					  	data.forEach(function(row){					
							//console.log(row);
							$clonele = $ele.clone().html(function(index,html){
								return html.replace('#comment#',row.comment).replace('#creator#',row.creator)
								.replace('#created_on#',row.created_on);
							});
							if(row.attachment){
								$clonele.find('.id-comment-attached')[0].style.display = 'block';
								$clonele.html(function(index,html){
									return html.replace('#id_comment_attached#',row.attachment.split("/")[4])
										.replace('#c_href#','https://s3.amazonaws.com/vizrules/'+row.attachment);
								});				
							}
							$this.append($clonele);
						  })
					  }
					  					  	
				  	}
				  })

				  		  
				})

				
			}
		});
	    $('#alertDetailModal').modal('show');  
	  }
	};

	let assginFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="assignlink" title="click to assign">'+value+'</a>';
	};

	window.assignEvents = {
	  'click .assignlink': function (e, value, row, index) {

	  	console.log(row);

	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/getanalystsbycompany',
		  	type: 'GET',
		  	data: JSON.stringify({}),
		  	success:function(data){

		  	  $('#hid_alertid').val(row.id);
		  	  $('#assginCommentTextArea').val('');
		  	  $('#assignCtl').empty();  	  
		  	  data.forEach(function(user){		  	  	
		  	  	$('#assignCtl').append('<option value="'+user.value+'">'+user.text+'</option>')
		  	  })


		  	  $.ajax({
				cache: false,
			  	url: $SCRIPT_ROOT+'/alerts/management/procescomments/'+row.id+"/Manager_Assign",
			  	type: 'GET',
			  	data: JSON.stringify({}),
			  	success:function(comments){
			  		console.log(comments);
			  		if(comments&&comments.length>0){
			  			$('#assginCommentTextArea').val(comments[0].comment);
			  			if(row.current_step!='Manager_Assign'){
			  				if(comments[0].assigned_to_fk){
				  				$('#assignCtl').val(comments[0].assigned_to_fk);
				  			}else{
			  					$('#assignCtl').empty();
			  					$('#assignCtl').append('<option value="'+comments[0].operated_by_fk+'">'+comments[0].username+'</option>');			  				
				  			}
			  			}		
			  		}
			  		if(row.current_step!='Manager_Assign'){
			  			$('#assginCommentTextArea').prop('disabled',true);
			  			$('#assignCtl').prop('disabled', true);	  
			  			$('#assignSaveBtn').prop('disabled', true);			
	  		  		}else{
	  		  			$('#assginCommentTextArea').prop('disabled',false);
	  		  			$('#assignCtl').prop('disabled', false);
	  		  			if(data.length>0){	  		  				
			  				$('#assignSaveBtn').prop('disabled', false);
	  		  			}else{
	  		  				$('#assignSaveBtn').prop('disabled', true);
	  		  			}
			  				 
	  		  		}
			  	}
			  });

		  	  $('#assginModal').modal('show'); 	 
		  	  
			  					  	
		  	}
		  }) 	

	  	   
	  }
	};

	var $alerttable = $('#alertTable').bootstrapTable({
		idField: 'id',
		url: $SCRIPT_ROOT+'/alerts/management/gettabledata/'+$('#alertMgt').data('start')+'/'+$('#alertMgt').data('end')+'/'+$('#alertMgt').data('type'),
  		pagination:true,
  		search:true,
	    columns: [{
	        field: 'id',
	        title: 'Item ID',
	        sortable:true,
	        events: idEvents,
          	formatter: idFormatter
	    }, {
            field: 'uid',
            title: 'Item Operate',
            align: 'center',
            events: operateEvents,
            formatter: operateFormatter
        }, {
	        field: 'account_key',
	        title: 'Account Key',
	        sortable:true,
	    }, {
	        field: 'trigger_rule',
	        title: 'Alert Rule',
	        sortable:true,
	    }, {
	        field: 'rule_type',
	        title: 'Rule Type',
	        sortable:true,
	    }, {
	        field: 'country_abbr',
	        title: 'Opposite Country',
	        sortable:true,
	    },{
	        field: 'country_name',
	        title: 'Country Name',
	        sortable:true,
	    },{
	        field: 'amount',
	        title: 'Trans Amount',
	        sortable:true,
	        formatter: function formatter(value, row, index, field) {
	        	return (value).toLocaleString('en-US', {
				  style: 'currency',
				  currency: 'USD',
				});
			},
	    },{
	        field: 'cnt',
	        title: 'Trans Cnt',
	        sortable:true,
	    },{
	        field: 'rule_status',
	        title: 'Status',
	        sortable:true,
	    },{
	        field: 'trans_month',
	        title: 'Month of Trans Date',
	        sortable:true,
	    },{
	        field: 'created_on',
	        title: 'Item Date',
	        sortable:true,
	    },{
	        field: 'finished_on',
	        title: 'Closed Date',
	        sortable:true,
	    },{
	        field: 'current_step',
	        title: 'Current Step',
	        sortable:true,
	    },{
	        field: 'username',
	        title: 'Operator',
	        /**
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
            **/
            align: 'center',
            events: assignEvents,
            formatter: assginFormatter
	    }],
	});

	statusChart.on('click', function(data){
		console.log(data);
		var old_start=$('#alertMgt').data('start');
		var old_end = $('#alertMgt').data('end');
        var aging = data.data.name;
        if(data.data.name.startsWith('Due')){
        	aging='30~30';
        }else if(data.data.name.endsWith('+')){
        	aging='31~1000000';
        }

		if(old_start==0&&old_end==0){
			$('#alertMgt').data('start',aging.split("~")[0]);
			$('#alertMgt').data('end',aging.split("~")[1]);
		}else{
			if(old_start==aging.split("~")[0]&&old_end==aging.split("~")[1]){//cancel select
				$('#alertMgt').data('start',0);
				$('#alertMgt').data('end',0);
			}else{
				$('#alertMgt').data('start',data.data.name.split("~")[0]);
				$('#alertMgt').data('end',data.data.name.split("~")[1]);
			}
		}
		
		$.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/gettabledata/'+$('#alertMgt').data('start')+'/'+$('#alertMgt').data('end')+'/'+$('#alertMgt').data('type'),
		  	type: 'GET',
		  	contentType:'application/json',
		  	success:function(data){
		  		$alerttable.bootstrapTable('load',data);	  	
		  	}
		  });

	});

	typeChart.on('click', function(data){
		console.log(data);
		var old_type=$('#alertMgt').data('type');

		if(old_type==0){
			$('#alertMgt').data('type',data.data.name);
		}else{
			if(old_type==data.data.name){//cancel select
				$('#alertMgt').data('type','0');
			}else{
				$('#alertMgt').data('type',data.data.name);
			}
		}
		$.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/gettabledata/'+$('#alertMgt').data('start')+'/'+$('#alertMgt').data('end')+'/'+$('#alertMgt').data('type'),
		  	type: 'GET',
		  	contentType:'application/json',
		  	success:function(data){
		  		$alerttable.bootstrapTable('load',data);	  	
		  	}
		  });
		
	});

	$('#alertTable').on('load-success.bs.table', function (data) {

		//$alerttable.bootstrapTable('hideColumn', 'username');
		//if($('#alertMgt').data('ismanager')=='False'){
		//	$alerttable.bootstrapTable('hideColumn', 'uid');
		//}

	});

	//$('#commentTextArea').bind('input propertychange', function() {
	//      $("#processCtl").bootstrapToggle('disable');
	//      if(this.value.length){
	//        $("#processCtl").bootstrapToggle('enable');
	//      }
	//});

	$( "#assginUserForm" ).submit(function( event ) {
	  event.preventDefault();

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/alerts/management/assignanalyst',
	  	type: 'POST',
	  	data: $( "#assginUserForm" ).serialize(),
	  	success:function(data){
	  		$('#assginModal').modal('hide');
	  		$alerttable.bootstrapTable('refresh');
	  		getBarChart();	  	
	  	}
	  });

	});

	$("#alertNoteForm").validate({
		ignore:"input[type=file]",
	    rules: {
	      commentTextArea:{
	      	required: true,
	      }
	    },
	});

	$( "#alertNoteForm" ).submit(function( event ) {
	  event.preventDefault();

	  if(!$("#alertNoteForm").valid()){
	  	return false;
	  }

	  $.ajax({
	  	cache: false,
	  	url: $SCRIPT_ROOT+'/alerts/management/addnote',
	  	type: 'POST',
	  	contentType:'application/json',
	  	data: JSON.stringify({'alert_id':$('#alertProcessModal').data('alertid'),'process_id':$('#alertProcessModal').data('processid'),
	  			'comment':$('#commentTextArea').val(),'status':$('#processCtl').prop('checked'),'attached':$('#commentAttachment').data('keyname')}),
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