function ready(jQuery) {
  var tooltip = {
    track: true,
    position: {
      my: "center top-28",
      at: "center top",
    }
  };

  $(".pheasant-fenced-code .cell.input .code")
    .append('<div class="pheasant-button-container"><button class="toggle input"></button></div>');
  $(".pheasant-fenced-code .cell.error .code")
    .append('<div class="pheasant-button-container"><button class="toggle error hide"></button></div>');

  $('.toggle.input').attr('title', 'Toggle Status Line').tooltip(tooltip).click(function(e) {
    $('.pheasant-fenced-code .input').toggleClass('hide')
  });

  $(".pheasant-fenced-code").each(function() {
    $(this).find('.cell.input').each(function() {
      var stdout = $(this).parent().find('.cell.stdout');
      if (stdout.length) {
        $('<button class="toggle output"></button>').prependTo($(this).find('.pheasant-button-container'))
          .attr('title', 'Toggle Stdout').tooltip(tooltip).click(function(e) {
            stdout.toggleClass('hide');
            $(this).toggleClass('hide');
          });
      };
      var stderr = $(this).parent().find('.cell.stderr').toggleClass('hide');
      if (stderr.length) {
        $('<button class="toggle error hide"></button>').prependTo($(this).find('.pheasant-button-container'))
          .attr('title', 'Toggle Stderr').tooltip(tooltip).click(function(e) {
            stderr.toggleClass('hide');
            $(this).toggleClass('hide');
          });
      };
    });

    $(this).find('.cell.error').toggleClass('hide').each(function(index, error) {
      $(this).find('.toggle.error').each(function() {
        $(this).attr('title', 'Toggle Traceback').tooltip(tooltip).click(function(e) {
          $(error).toggleClass('hide');
          $(this).toggleClass('hide');
        });

      })
    });
  });

  $('.pheasant-fenced-code .report .count').attr('title', 'Cell Number').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .start').attr('title', 'Evaluated at').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .cell-time').attr('title', 'Cell Execution Time').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .page-time').attr('title', 'Page Execution Time').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .total-time').attr('title', 'Total Execution Time').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .total-count').attr('title', 'Total Execution Count').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .kernel').attr('title', 'Kernel Name').tooltip(tooltip).css("cursor", "pointer");
}

$(ready);
