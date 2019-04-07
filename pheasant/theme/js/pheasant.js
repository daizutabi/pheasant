function ready(jQuery) {
  $('<div class="pheasant-button-container"><button class="toggle-button"></button></div>')
    .appendTo(".pheasant-fenced-code .input");
  $('.toggle-button').attr('title', 'Toggle Report').tooltip({
    hide: true,
    position: {
      my: "right+5 top-28",
      at: "right top",
    }
  }).click(function(e) {
    $('.pheasant-fenced-code .input').toggleClass('hide')
  });

  $(".pheasant-fenced-code .stdout").each(function() {
    if ($(this).text().match(/\n/)) {
      $('<div class="pheasant-button-container"><button class="toggle-button"></button></div>')
        .appendTo($(this));


      console.log($(this).text());
    }
  });


}

$(ready);
