odoo.define('record_authenticate_by_user.main', function (require) {
    "use strict";
    var FormController = require('web.FormController');
    var session = require('web.session');
    var rpc = require('web.rpc');
    
    FormController.include({
    	_onSave: function (ev) {
	        var self = this;
	        var model = self.modelName;
			var passkey = ""
			var locale = {
			    OK: 'Confirm',
			    CONFIRM: 'Confirm',
			    CANCEL: 'Cancel'
			};
			
			rpc.query({
                model: 'record.authenticate',
                method: 'check_model',
                args: [model],
            })
            .then(function (result) {
            	if(result == '1'){
            		bootbox.addLocale('custom', locale);
        			bootbox.prompt({
        		        title: "Confirm your account to update the record", 
        		        locale: 'custom',
        		        inputType: "password",
        		        placeholder: "Enter your password",
        		        required: true,
        		        callback: function(result) {
        		        	passkey = result
        		        	rpc.query({
        	                    model: 'record.authenticate',
        	                    method: 'autenticate_user',
        	                    args: [session.origin, session.db, session.username, passkey, model],
        	                })
        	                .then(function (result) {
        	                	if(result == '1'){
        	                		ev.stopPropagation(); // Prevent x2m lines to be auto-saved
        	                		self.saveRecord();
        	                	}else{
        	                		alert("User validation failured. Please try again.");
        	                	}
        	                });
        		        }
        		    });
            	}else{
            		ev.stopPropagation(); // Prevent x2m lines to be auto-saved
            		self.saveRecord();
            	}
            });
	    },
	});
});