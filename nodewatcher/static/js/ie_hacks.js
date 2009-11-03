$(document).ready(function () {
  // Workaround for IE handling of change event which is not triggered until input element loses its focus
  $('input:radio,input:checkbox').click(function () {
    this.blur();
    this.focus();
  });
}
