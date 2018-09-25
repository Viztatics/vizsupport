$(function(){
	var company_id=$('#accordion').data('firstcom');

	var getRuleByCompany = function(company_id){

	  	$.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/datacenter/rules/getRuleByCompany/'+company_id,
		  	type: 'GET',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){
		  		console.log(data);
		  		$ele = $('#group_form_'+company_id).find('.form-group').css('display','block').clone();
		  		$('#group_form_'+company_id).empty();
		  		$.each(data,function(key, el) {
		  			$clonele = $ele.clone().html(function(index,html){
									return html.replace('#rule_group#',key+":").replace('#rule#',el[0].rule_code)
									.replace('#chk_id#','chk_'+key+'_'+el[0].rule_code)
									.replace('#chk_name#','chk_'+key).replace('#rule_id#',el[0].id);
								});
		  			$('#group_form_'+company_id).append($clonele);
		  			$.each(el,function(index, obj) {
		  				//console.log(index);
		  				//console.log(obj);
		  				if(index!=0){
		  					$clonele = $ele.clone().html(function(index,html){
									return html.replace('#rule_group#','').replace('#rule#',obj.rule_code)
									.replace('#chk_id#','chk_'+key+'_'+obj.rule_code)
									.replace('#chk_name#','chk_'+key).replace('#rule_id#',obj.id);
								});
		  					$('#group_form_'+company_id).append($clonele);
		  				}
		  				
		  			});
		  		});

		  	}
		})

	};

	$('#ruleDetailModal').on('hidden.bs.modal', function (e) {
		var $this = $(this);
		$this.find('#myModalLabel').text('Rule Code : #detail_rule_code#');
		$this.find('.table td:first').text('#detail_desc#');
		$this.find('.table td:eq(1)').text('#detail_param#');
		$this.find('.table td:last').text('#detail_other#');
	  // do something...
	})

	$('#ruleDetailModal').on('show.bs.modal', function (event) {
	  var $this = $(this);
	  var button = $(event.relatedTarget) // Button that triggered the modal
	  var recipient = button.data('ruleid') // Extract info from data-* attributes
	  console.log('trigger rule id:'+recipient);
	  $.ajax({
			cache: false,
		  	url: $SCRIPT_ROOT+'/datacenter/rules/'+recipient,
		  	type: 'GET',
		  	contentType:'application/json',
		  	data: JSON.stringify({}),
		  	success:function(data){
		  		console.log(data);
		  		$this.find('#myModalLabel').html(function(index,html){return html.replace('#detail_rule_code#',data.rule_code);});
		  		var detail_other = '<strong>Alert Or Case : </strong> '+data.rule_type+'</br>'+
		  		'<strong>Schedule : </strong> '+data.schedule+'</br>'+
		  		'<strong>Eval Time : </strong> '+data.pre_post_EOD+'</br>'+
		  		'<strong>Schedule Freq : </strong> '+data.schedule+'</br>';
		  		var detail_parameters = '';
		  		detail_parameters+=data.customer_type?'List of Customer Types separated by comma. Use -ALL- for All. =\''+data.customer_type+'\'</br>':'';
		  		detail_parameters+=data.customer_risk_class?'List of Risk Classes separated by comma. Use -ALL- for All. =\''+data.customer_risk_class+'\'</br>':'';
		  		detail_parameters+=data.min_trans_no?'Minimum Total Transaction Count =\'' +data.min_trans_no+'\'</br>':'';
		  		detail_parameters+=data.min_ind_trans_amt?'Minimum Total Transaction Amount (-1 if no minimum) =\'' +data.min_ind_trans_amt+'\'</br>':'';
		  		detail_parameters+=data.max_ind_trans_amt?'Maximum Total Transaction Amount (-1 if no maximum) =\'' +data.max_ind_trans_amt+'\'</br>':'';
		  		detail_parameters+=data.min_agg_trans_amt?'Minimum Transaction Amount (-1 if no minimum) =\'' +data.min_agg_trans_amt+'\'</br>':'';
		  		detail_parameters+=data.max_agg_trans_amt?'Maximum Transaction Amount (-1 if no maximum) =\'' +data.max_agg_trans_amt+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		detail_parameters+=data.cash_ind?'Cash or non-Cash (inbound). 1 for Cash, 0 for NonCash, 2 for both =\'' +data.cash_ind+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		detail_parameters+=data.additional?'High risk Customer Types (MSB/FCB/CIB/PSP/NBFI) =\'' +data.additional+'\'</br>':'';
		  		$this.find('.table').html(function(index,html){
		  			return html.replace('#detail_desc#',data.rule_description).replace('#detail_other#',detail_other).replace('#detail_param#',detail_parameters);
		  		});
		  	}
	  })
	  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
	  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
	  //var modal = $(this)
	  //modal.find('.modal-title').text('New message to ' + recipient)
	  //modal.find('.modal-body input').val(recipient)
	})

	$('.panel-collapse').on('show.bs.collapse', function () {
	  	$this = $(this);
	  	var company_id = $this.prop('id').split('_')[1];
	  	console.log(company_id);
	  	getRuleByCompany(company_id);

	})

	var init = function(){
		getRuleByCompany(company_id);
	};

	init();


})