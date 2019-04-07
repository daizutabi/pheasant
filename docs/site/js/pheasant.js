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


}

$(ready);
