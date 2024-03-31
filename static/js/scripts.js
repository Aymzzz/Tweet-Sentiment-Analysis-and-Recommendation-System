// $("form[name=signup_form").submit(function (e) {
//   var $form = $(this);
//   var $error = $form.find(".error");
//   var data = $form.serialize();

//   $.ajax({
//     url: "/user/signup",
//     type: "POST",
//     data: data,
//     dataType: "json",
//     success: function (resp) {
//       window.location.href = "/dashboard/";
//     },
//     error: function (resp) {
//       $error.text(resp.responseJSON.error).removeClass("error--hidden");
//     },
//   });

//   e.preventDefault();
// });

$("form[name=signup_form]").submit(function (e) {
  var $form = $(this);
  var $error = $form.find(".error");
  var data = $form.serialize();

  $.ajax({
    url: "/user/signup",
    type: "POST",
    data: data,
    dataType: "json",
    success: function (resp) {
      window.location.href = "/dashboard/";
    },
    error: function (xhr, status, error) {
      var errorMessage;
      if (xhr.responseJSON && xhr.responseJSON.error) {
        errorMessage = xhr.responseJSON.error;
      } else {
        errorMessage = "An error occurred";
      }
      $error.text(errorMessage).removeClass("error--hidden");
    },
  });

  e.preventDefault();
});
