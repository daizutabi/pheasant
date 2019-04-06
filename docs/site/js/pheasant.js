function ready(jQuery) {
  $('<div class="pheasant-input-button-container"><button class="pheasant-input-button"></button></div>')
    .appendTo(".pheasant-fenced-code .input");
  $('.pheasant-input-button').click(function(e) {
    $('.pheasant-fenced-code').toggleClass('report-hide')
  });
}

$(ready);
