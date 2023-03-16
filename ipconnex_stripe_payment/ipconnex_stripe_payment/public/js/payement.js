frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        frm.add_custom_button(__('Process Invoice'), function() {
            $('button[data-label="Process%20Invoice"]').prop('disabled', true);
            
            if(frm.doc.status !== 'Unpaid' && frm.doc.status !== 'Overdue') {
                 frappe.msgprint('This invoice is ' + frm.doc.status)
                 return 0;
            }
            frappe.msgprint('Validation done')
            $('button[data-label="Process%20Invoice"]').prop('disabled', false);
        });
    }
});


