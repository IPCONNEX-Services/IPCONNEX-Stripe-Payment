frappe.ui.form.on("User Subscription", {
  refresh: function (frm) {
    $("button[data-fieldname='subscribe']")
      .off("click")
      .on("click", function () {
        console.log("Subscribe now");
      });
  },
});
