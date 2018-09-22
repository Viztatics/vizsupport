$(function(){
	var company_id=$('#accordion').data('firstcom');

  	$.ajax({
		cache: false,
	  	url: $SCRIPT_ROOT+'/datacenter/rules/getRuleByCompany/'+company_id,
	  	type: 'GET',
	  	contentType:'application/json',
	  	data: JSON.stringify({}),
	  	success:function(data){
	  		console.log(data);
	  		$ele = $('#group_form_'+company_id).find('.form-group').css('display','block').clone();
	  		$('#group_form_'+$('#accordion').data('firstcom')).empty();
	  		$.each(data,function(key, el) {
	  			$clonele = $ele.clone().html(function(index,html){
								return html.replace('#rule_group#',key+":").replace('#rule#',el[0].rule_code)
								.replace('#chk_id#','chk_'+key+'_'+el[0].rule_code)
								.replace('#chk_name#','chk_'+key);
							});
	  			$('#group_form_'+company_id).append($clonele);
	  			$.each(el,function(index, obj) {
	  				//console.log(index);
	  				//console.log(obj);
	  				if(index!=0){
	  					$clonele = $ele.clone().html(function(index,html){
								return html.replace('#rule_group#','').replace('#rule#',obj.rule_code)
								.replace('#chk_id#','chk_'+key+'_'+obj.rule_code)
								.replace('#chk_name#','chk_'+key);
							});
	  					$('#group_form_'+company_id).append($clonele);
	  				}
	  				
	  			});
	  		});

	  	}
	})
})