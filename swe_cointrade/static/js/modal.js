function showModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "block";
  }
  
  function hideModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "none";
  }
  
  document.addEventListener("DOMContentLoaded", function () {
    var modalTriggers = document.querySelectorAll("[data-toggle='modal']");
    modalTriggers.forEach(function (trigger) {
      var target = trigger.getAttribute("data-target");
      trigger.addEventListener("click", function () {
        showModal(target);
      });
    });
  
    var closeButtons = document.querySelectorAll("[data-dismiss='modal']");
    closeButtons.forEach(function (button) {
      var modal = button.closest(".modal");
      button.addEventListener("click", function () {
        hideModal(modal.id);
      });
    });
  });