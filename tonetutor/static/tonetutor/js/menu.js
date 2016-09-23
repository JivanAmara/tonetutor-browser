;
$(document).ready(function() {
    $('#auth-menu').mouseenter(function() {
        $('#site-menu').show();; 
    });
    $('#auth-menu').mouseleave(function() {
        $('#site-menu').hide();
    });
    document.getElementById('shareBtn').onclick = function() {
        FB.ui({
          method: 'share',
          display: 'popup',
          href: domain + '/',
        }, function(response){});
    }
});

/* Facebook share button setup */
window.fbAsyncInit = function() {
  FB.init({
    appId      : fbAppId,
    // Test ID (test-01.mandarintt.com): '1163946780339472'
    // Live ID (www.mandarintt.com): '1163946780339471'
    xfbml      : true,
    version    : 'v2.7'
  });
};

(function(d, s, id){
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {return;}
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
