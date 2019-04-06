function ready(jQuery) {
  $('<div class="pheasant-input-button-container"><button class="toggle-report-button"></button></div>')
    .appendTo(".pheasant-fenced-code .input");
  $('.toggle-report-button').attr('title', 'Toggle Report');
  $('.toggle-report-button').tooltip({hide: true, position:{
			my:"right+5 top-28",
			at:"right top",
  }});
  $('.toggle-report-button').click(function(e) {
    $('.pheasant-fenced-code').toggleClass('report-hide')
  });
}

$(ready);
