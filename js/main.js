$(function(){

  let css_selector = document.getElementById('twitter-text-main');
  let css_fontsize = window.getComputedStyle(css_selector, null).getPropertyValue('font-size');
  let css_ls = window.getComputedStyle(css_selector, null).getPropertyValue('letter-spacing');

  var ws = new WebSocket("ws://127.0.0.1:10356/");
  ws.onmessage = function(message){

    var window_w = window.innerWidth;

    var span = document.createElement('span');

    span.style.position = 'absolute';
    span.style.top = '-1000px';
    span.style.left = '-1000px';

    span.style.whiteSpace = 'nowrap';

    span.innerHTML = message.data;

    span.style.fontSize = css_fontsize;
    span.style.letterSpacing = css_ls;

    document.body.appendChild(span);

    var text_width = span.clientWidth;
    var text_width_int = parseInt(text_width);
    var text_scroll = window_w - text_width_int

    span.parentElement.removeChild(span);

    if (text_width_int >= window_w) {

      $("#twitter-text-main").text(message.data);
      $('#twitter-text-main').animate({opacity: 1},{queue: false,duration: 2000,easing: 'swing'});
      $('#twitter-text-main').animate({marginLeft: 0},{queue: false,duration: 2000,easing: 'swing'}).delay(3000);
      $('#twitter-text-main').animate({marginLeft: text_scroll-10},{duration: text_width_int*2,easing: 'linear'}).delay(3000);
      $('#twitter-text-main').animate({opacity: 0},{duration: 2000,complete: function(){ws.send('RT'),$('#twitter-text-main').css('margin-left','250px');}});

    }else{

      $("#twitter-text-main").text(message.data);
      $('#twitter-text-main').animate({opacity: 1},{queue: false,duration: 2000,easing: 'swing'});
      $('#twitter-text-main').animate({marginLeft: 0},{queue: false,duration: 2000,easing: 'swing'}).delay(5000);
      $('#twitter-text-main').animate({opacity: 0},{duration: 2000,complete: function(){ws.send('RT'),$('#twitter-text-main').css('margin-left','250px');}});

    }
  }
})
