
$("#followButton").click(function(){
    var username = document.getElementById("username").innerHTML;
    var action = document.getElementById("followButton");
    if (action.value == 'Unfollow') {
        action.value = 'Follow';
    } else {
        action.value = 'Unfollow';
    }
    $.ajax({
      url: "/follow_action",
      type: "get",
      data: {act: action.value, username: username},
      success: function(response) {
        $("#followButton").html(response);
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
    return true;
});



$(".like").click(function(){
    var post_id = $(this).val();
    var action = $(this).attr("alt");
    var like_count = document.getElementById("like" + post_id);
    $.ajax({
      url: "/like_action",
      type: "get",
      data: {act: action, post_id: post_id},
      success: function(response) {
        $(like_count).html(response);
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
    if (action == 'like') {
        this.setAttribute('src', '../static/assets/like.png');
        this.setAttribute('alt', 'unlike');
    } else {
        this.setAttribute('src', '../static/assets/unlike.png');
        this.setAttribute('alt', 'like');
    }

    return true;
});

$(".comment").click(function(){
    var post_id = $(this).attr("alt");
    var comment = document.getElementById(post_id).value;
    $.ajax({
      url: "/add_comment",
      type: "get",
      data: {comment: comment, post_id: post_id},
      success: function(response) {
        $(this.innerHTML).html(response);
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });

    return true;
});