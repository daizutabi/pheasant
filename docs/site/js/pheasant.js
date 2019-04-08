function ready(jQuery) {
  var tooltip = {
    hide: true,
    position: {
      my: "right+5 top-28",
      at: "right top",
    }
  };

  $('<div class="pheasant-button-container"><button class="toggle-button"></button></div>')
    .appendTo(".pheasant-fenced-code .input");
  $('.toggle-button').attr('title', 'Toggle Report').tooltip(tooltip).click(function(e) {
    $('.pheasant-fenced-code .input').toggleClass('hide')
  });

  $(".pheasant-fenced-code .stdout").each(function(i, element) {
    if ($(this).text().match(/\n/)) {
      $('<div class="pheasant-button-container"><button class="toggle-button"></button></div>')
        .appendTo($(this));
      $(this).find('.toggle-button').attr('title', 'Toggle Output').tooltip(tooltip).click(function(e) {
        $(element).toggleClass('hide');
      });
    }
  });

  $(".pheasant-fenced-code .error").each(function(i, element) {
    if ($(this).text().match(/\n/)) {
      $('<div class="pheasant-button-container"><button class="toggle-button"></button></div>')
        .appendTo($(this));
      $(this).find('.toggle-button').attr('title', 'Toggle Traceback').tooltip(tooltip).click(function(e) {
        $(element).toggleClass('hide');
      });
    }
  });

  $('.pheasant-fenced-code .report .count').attr('title', 'Page Cell Number').tooltip(tooltip);
  $('.pheasant-fenced-code .report .start').attr('title', 'Evaluated at').tooltip(tooltip);
  $('.pheasant-fenced-code .report .cell').attr('title', 'Cell Execution Time').tooltip(tooltip);
  $('.pheasant-fenced-code .report .page').attr('title', 'Page Execution Time').tooltip(tooltip);
  $('.pheasant-fenced-code .report .total').attr('title', 'Total Execution Time').tooltip(tooltip);
  $('.pheasant-fenced-code .report .total-count').attr('title', 'Total Execution Count').tooltip(tooltip);
  $('.pheasant-fenced-code .report .kernel').attr('title', 'Kernel Name').tooltip(tooltip);
}

$(ready);
