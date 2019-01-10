$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });


	let barChart = echarts.init(document.getElementById('barChart'));

	let barOption = {
		title : {
	        text: 'Alerts Rule Group Distribution',
	        x:'center'
	    },
	    tooltip : {
	        trigger: 'axis',
	        axisPointer : {            
	            type : 'line'        
	        }
	    },
	    legend: {
	    	show:false,
	    	orient: 'vertical',
        	x : 'right',
	        data:[]
	    },
	    xAxis : [
	        {
	        	name : 'alerts',
	            type : 'value',
	            data : []
	        }
	    ],
	    yAxis : [
	        {
	        	name : 'Rule Group',
	            type : 'category',
	            data : []
	        }
	    ],
	    series : [
	        {
	            name:'Alerts',
	            type:'bar',
	            itemStyle: {
				    normal: {
				       //color:'#ff3333',
				    },
				},
	            data:[],
	        }
	    ]
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
					console.log(data);
					barOption.yAxis[0].data=[];
					barOption.series[0].data=[];
					data.forEach(function(ele){	
						barOption.yAxis[0].data.push(ele[1]);
						barOption.series[0].data.push({'name':ele[1],'value':ele[0]});	  	  	
				  	});
					
					barChart.setOption(barOption);
				}			
			}
		});

	};

	barChart.on('click', function(data){
		console.log(data);
		var old_status=$('#alertMgt').data('status');
		if(old_status==0){
			$('#alertMgt').data('status',data.data.name);
		}else{
			if(old_status==data.data.name){//cancel select
				$('#alertMgt').data('status','0');
			}else{
				$('#alertMgt').data('status',data.data.name);
			}
		}
		$.ajax({
		  	cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/gettabledata/'+$('#alertMgt').data('status'),
		  	type: 'GET',
		  	contentType:'application/json',
		  	success:function(data){
		  		$alerttable.bootstrapTable('load',data);	  	
		  	}
		  });
		
	});

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

				$.ajax({
			    	url: $SCRIPT_ROOT+'/alerts/management/getTrans/'+$("#altAcckey").text(),
			    	type: 'get',
			    	dataType: 'JSON',
			    	data: {},
			    })
			    .done(function(result) {
			    	$('#transTable').bootstrapTable({
						idField: 'id',
						exportDataType: 'all',
						data:result,
				  		pagination:true,
					    columns: [{
						          field: 'id',
						          title: 'Trans Num',
						          align: 'center',
						          //formatter: checkboxFormatter
						}, {
					        field: 'customer_id',
					        title: 'Customer Id',
					    }, {
				            field: 'account_key10',
				            title: 'Account Key',
				        }, {
					        field: 'trans_amt',
					        title: 'Trans Amount',
					    }, {
					        field: 'trans_code',
					        title: 'Trans Code',
					    }, {
					        field: 'is_cash_trans',
					        title: 'Is Cash Trans',
					    },{
					        field: 'trans_date',
					        title: 'Trans Date',
					    },{
					        field: 'bene_name',
					        title: 'Beneficial Name',
					    },{
					        field: 'bene_country',
					        title: 'Beneficial Country',
					    },{
					        field: 'bene_bank_country',
					        title: 'Beneficial Bank Country',
					    },{
					        field: 'by_order_name',
					        title: 'By Order Name',
					    },{
					        field: 'by_order_country',
					        title: 'By Order Country',
					    },{
					        field: 'by_order_bank_country',
					        title: 'By Order Bank Country',
					    }],
					});
					$('#transTable').bootstrapTable('load', result);
			    });
				
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
			  		$('#assignCtl').prop('disabled', false);
			  		$("#assignCtl").val(comments[0].operated_by_fk);	
			  		$('#assginCommentTextArea').prop('disabled',false);  		  			
  		  			if(data.length>0){	  		  				
		  				$('#assignSaveBtn').prop('disabled', false);
  		  			}else{
  		  				$('#assignSaveBtn').prop('disabled', true);
  		  			}
			  		
			  	}
			  });

		  	  $('#assginModal').modal('show'); 	 
		  	  
			  					  	
		  	}
		  }) 	

	  	   
	  }
	};

	let checkboxFormatter=function(value, row, index) {
		if(row.current_step!='Manager_Assign'){
			return {
	            disabled: true
	        };
		}
	  	return value;
	};

	var $alerttable = $('#alertTable').bootstrapTable({
		idField: 'id',
		url: $SCRIPT_ROOT+'/alerts/management/gettabledata/'+$('#alertMgt').data('status'),
  		pagination:true,
  		search:true,
	    columns: [{
		          field: 'state',
		          checkbox: true,
		          align: 'center',
		          valign: 'middle',
		          //formatter: checkboxFormatter
		}, {
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
	        field: 'cycle_name',
	        title: 'Cycle Name',
	        sortable:true,
	    },{
	        field: 'run_name',
	        title: 'Run Name',
	        sortable:true,
	    },{
	        field: 'product_type',
	        title: 'Product Type',
	        sortable:true,
	    },{
	        field: 'customer_type',
	        title: 'Customer Type',
	        sortable:true,
	    },{
	        field: 'customer_risk_level',
	        title: 'Customer Risk Level',
	        sortable:true,
	    },{
	        field: 'current_threshold',
	        title: 'Current Threshold',
	        sortable:true,
	    },{
	        field: 'testing_threshold',
	        title: 'Testing Threshold',
	        sortable:true,
	    },{
	        field: 'data_id',
	        title: 'Data Id',
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

    $('#alertTable').on('check.bs.table uncheck.bs.table check-all.bs.table uncheck-all.bs.table', () => {
    	
	    $('#assginAlertBtn').prop('disabled', !$('#alertTable').bootstrapTable('getSelections').length);
	});

	$('#assginAlertBtn').click(() => {
		ids = $.map($('#alertTable').bootstrapTable('getSelections'), function(item, index) {
    		return item.id;
    	});
    	//items = $.map($('#alertTable').bootstrapTable('getSelections'), function(item, index) {
    	//	return item;
    	//});
	    console.log(ids);

	    //show pop window

	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/getanalystsbycompany',
		  	type: 'GET',
		  	data: JSON.stringify({}),
		  	success:function(data){

		  	  $('#hid_alertid').val(ids);
		  	  $('#assginCommentTextArea').val('');
		  	  $('#assignCtl').empty();  	  
		  	  data.forEach(function(user){		  	  	
		  	  	$('#assignCtl').append('<option value="'+user.value+'">'+user.text+'</option>')
		  	  });

		  	  $('#assginModal').modal('show'); 	 
		  	  
			  					  	
		  	}
		  }) 	 
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
	  		//$('#assginAlertBtn').prop('disabled',true);
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

	let initTransTable=function(){
		$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/alerts/management/initTrans',
		  	type: 'GET',
		  	data: JSON.stringify({}),
		  	success:function(data){ 	 
		  	  
			  					  	
		  	}
		  })
	};

	let init=function(){

		if($('#alertMgt').data('ismanager')=='True'){		
			getBarChart();
			$("#toolbar").css('display','block');
		}else{
			$('#barChart').css('display', 'none');
			$("#toolbar").css('display','none');
		}
				

	};

	init();
  

})