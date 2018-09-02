$(function(){

	$(document).ajaxStop(function () {
        $('#mask').removeClass('lmask');	
    });

    $(document).ajaxStart(function () {
        $('#mask').addClass('lmask');	
    });

	let operateFormatter=function(value, row, index) {
	  return '<a href="javascript:void(0)" class="btn btn-primary btn-sm note" title="Add note">Add Note</a>';
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

	var $alerttable = $('#alertTable').bootstrapTable({
		idField: 'id',
		url: $SCRIPT_ROOT+'/alerts/archive/gettabledata',
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
	    }],
	});

	$('#alertTable').on('load-success.bs.table', function (data) {

		//$alerttable.bootstrapTable('hideColumn', 'username');
		//if($('#alertMgt').data('ismanager')=='False'){
		//	$alerttable.bootstrapTable('hideColumn', 'uid');
		//}

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
  

})