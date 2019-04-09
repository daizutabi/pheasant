function ready(jQuery) {
  var tooltip = {
    hide: true,
    position: {
      my: "right+5 top-28",
      at: "right top",
    }
  };

  $(".pheasant-fenced-code .cell.input .code")
    .append('<div class="pheasant-button-container"><button class="toggle input"></button></div>');
  $('.toggle.input').attr('title', 'Toggle Status Line').tooltip(tooltip).click(function(e) {
    $('.pheasant-fenced-code .input').toggleClass('hide')
  });

  $(".pheasant-fenced-code .cell.error .code")
    .append('<div class="pheasant-button-container"><button class="toggle error"></button></div>');
  $('.toggle.error').attr('title', 'Toggle Traceback').tooltip(tooltip).click(function(e) {
    $('.pheasant-fenced-code .error').toggleClass('hide')
  });

  $(".pheasant-fenced-code").each(function() {
    $(this).find('.cell.stdout').each(function(i, stdout) {
      $(stdout).prevAll('.cell.input').each(function(i, input) {
        $(input).find('.pheasant-button-container').prepend('<button class="toggle output"></button>');
        $(input).find('.toggle.output').attr('title', 'Toggle Stdout').tooltip(tooltip).click(function(e) {
          $(stdout).toggleClass('hide');
          $(this).toggleClass('hide');
        });
      });
    });
    $(this).find('.cell.stderr').each(function(i, stderr) {
      $(stderr).prevAll('.cell.input').each(function(i, input) {
        $(input).find('.pheasant-button-container').prepend('<button class="toggle error"></button>');
        $(input).find('.toggle.error').attr('title', 'Toggle Stderr').tooltip(tooltip).click(function(e) {
          $(stderr).toggleClass('hide');
          $(this).toggleClass('hide');
        });
      });
    });
  });

  $('.pheasant-fenced-code .report .count').attr('title', 'Page Cell Number').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .start').attr('title', 'Evaluated at').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .cell-time').attr('title', 'Cell Execution Time').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .page-time').attr('title', 'Page Execution Time').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .total-time').attr('title', 'Total Execution Time').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .total-count').attr('title', 'Total Execution Count').tooltip(tooltip).css("cursor", "pointer");
  $('.pheasant-fenced-code .report .kernel').attr('title', 'Kernel Name').tooltip(tooltip).css("cursor", "pointer");
}

$(ready);
