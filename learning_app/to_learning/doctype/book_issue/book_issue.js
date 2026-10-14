// Copyright (c) 2026, TEST and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Book Issue", {
// 	refresh(frm) {

// 	},
// });
// Copyright (c) 2026, TEST and contributors
// For license information, please see license.txt

frappe.ui.form.on('Book Issue', {
    // ==================== Form Events ====================
    
    onload: function(frm) {
        // عند فتح نموذج جديد
        if (frm.is_new()) {
            // ضبط Issue Date = اليوم
            if (!frm.doc.issue_date) {
                frm.set_value('issue_date', frappe.datetime.get_today());
            }
            // ضبط Expected Return Date = اليوم + 14 يوم
            if (!frm.doc.expected_return_date) {
                frm.set_value(
                    'expected_return_date',
                    frappe.datetime.add_days(frappe.datetime.get_today(), 14)
                );
            }
        }
    },

    refresh: function(frm) {
        // زر مخصص: "إرجاع جميع الكتب"
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Active') {
            frm.add_custom_button(__('إرجاع جميع الكتب'), function() {
                frappe.confirm(
                    'هل تريد تسجيل إرجاع جميع الكتب بتاريخ اليوم؟',
                    function() {
                        let today = frappe.datetime.get_today();
                        (frm.doc.books || []).forEach(function(row) {
                            if (!row.return_date) {
                                frappe.model.set_value(
                                    row.doctype, row.name, 
                                    'return_date', today
                                );
                            }
                        });
                        frm.refresh_field('books');
                        frappe.show_alert({
                            message: 'تم تسجيل إرجاع جميع الكتب',
                            indicator: 'green'
                        });
                    }
                );
            });
        }
    },

    // ==================== Member Events ====================
    
    member: function(frm) {
        if (!frm.doc.member) return;
        
        // جلب عدد الاستعارات النشطة لهذا العضو
        frappe.call({
            method: 'frappe.client.get_count',
            args: {
                doctype: 'Book Issue',
                filters: {
                    member: frm.doc.member,
                    docstatus: 1,
                    status: 'Active'
                }
            },
            callback: function(r) {
                if (r.message !== undefined) {
                    let count = r.message;
                    let color = count >= 3 ? 'red' : (count >= 2 ? 'orange' : 'green');
                    let msg = `الاستعارات النشطة: ${count} / 3`;
                    
                    if (count >= 3) {
                        frappe.msgprint({
                            title: 'تحذير',
                            indicator: 'red',
                            message: `هذا العضو وصل للحد الأقصى (${count} استعارات).`
                        });
                    }
                    
                    frm.dashboard.set_headline_alert(
                        `<span class="indicator ${color}">${msg}</span>`
                    );
                }
            }
        });
    },

    // ==================== Status Events ====================
    
    status: function(frm) {
        // عند تغيير Status، نُحدّث الواجهة
        frm.refresh_fields();
    }
});


// ==================== Child Table Events ====================

frappe.ui.form.on('Book Issue Item', {
    // عند إضافة صف جديد في Books
    books_add: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        // ضبط Issue Date تلقائياً
        if (!row.issue_date && frm.doc.issue_date) {
            frappe.model.set_value(cdt, cdn, 'issue_date', frm.doc.issue_date);
        }
        
        // ضبط Due Date تلقائياً = Issue Date + 14
        if (!row.due_date && frm.doc.issue_date) {
            frappe.model.set_value(
                cdt, cdn, 
                'due_date', 
                frappe.datetime.add_days(frm.doc.issue_date, 14)
            );
        }
        
        // ضبط Status = Issued
        if (!row.status) {
            frappe.model.set_value(cdt, cdn, 'status', 'Issued');
        }
    },

    // عند تغيير Article
    article: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        if (row.article) {
            // جلب بيانات الكتاب
            frappe.db.get_value('Article', row.article, 
                ['article_name', 'author', 'status'], 
                function(data) {
                    if (data) {
                        if (data.status !== 'Available') {
                            frappe.msgprint({
                                title: 'تنبيه',
                                indicator: 'orange',
                                message: `الكتاب "${data.article_name}" حالته ${data.status}.`
                            });
                        }
                        // عرض رسالة نجاح
                        frappe.show_alert({
                            message: `تم اختيار: ${data.article_name}`,
                            indicator: 'blue'
                        });
                    }
                }
            );
        }
    },

    // عند تغيير Issue Date في الصف
    issue_date: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        // حدّث Due Date تلقائياً
        if (row.issue_date) {
            frappe.model.set_value(
                cdt, cdn,
                'due_date',
                frappe.datetime.add_days(row.issue_date, 14)
            );
        }
    },

    // عند تغيير Return Date
    return_date: function(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        
        // احسب Fine تلقائياً إذا كان هناك تأخير
        if (row.return_date && row.due_date) {
            let days_late = frappe.datetime.get_diff(
                row.return_date, 
                row.due_date
            );
            
            if (days_late > 0) {
                frappe.model.set_value(cdt, cdn, 'days_late', days_late);
                
                // 5 ريال/يوم غرامة
                let fine = days_late * 5;
                frappe.model.set_value(cdt, cdn, 'fine_amount', fine);
                
                frappe.show_alert({
                    message: `تأخير ${days_late} يوم — غرامة ${fine} IQD`,
                    indicator: 'red'
                });
            } else {
                frappe.model.set_value(cdt, cdn, 'days_late', 0);
                frappe.model.set_value(cdt, cdn, 'fine_amount', 0);
            }
        }
    }
});