$(document).ready(function () {
    var ENTER_KEY = 13;
    var popupLoading = '<i class="notched circle loading icon green"></i> Loading...';
    var message_count = 0;

    function scrollToBottom() {
        var $messages = $('.messages');
        $messages.scrollTop($messages[0].scrollHeight);
    }

    function new_message(e) {
        var $textarea = $('#message-textarea');
        var message_body = $textarea.val().trim();
        if (e.which === ENTER_KEY && !e.shiftKey && message_body) {
            e.preventDefault(); // 阻止默认行为：换行
            socket.emit('new message', message_body);
            $textarea.val('')
        }
    }

    function activateSemantics() {
        $('.ui.dropdown').dropdown();
        $('.pop-card').popup({
            inline: true,
            on: 'hover',
            hoverable: true,
            html: popupLoading,
            delay: {
                show: 200,
                hide: 200
            },
            onShow: function () {
                var popup = this;
                popup.html(popupLoading);
                $.get({
                    url: $(popup).prev().data('href')
                }).done(function (data) {
                    popup.html(data);
                }).fail(function () {
                    popup.html('Failed to load profile.');
                });
            }
        });
    }

    // submit message
    $('#message-textarea').on('keydown', new_message);

    // submit snippet
    $('#snippet-button').on('click', function () {
        var $snippet_textarea = $('#snippet-textarea');
        var message = $snippet_textarea.val();
        if (message.trim() !== ''){
            socket.emit('new message', message);
            $snippet_textarea.val('');
        }
    });

    // open message modal on mobile
    $("#message-textarea").focus(function () {
        if (screen.width < 600) {$('#mobile-new-message-modal').modal('show');
        $('#mobile-message-textarea').focus()}
    });
    $('#send-button').on('click', function () {
        var $mobile_textarea = $('#mobile-message-textarea');
        var message = $mobile_textarea.val();
        if (message.trim() !== '') {
            socket.emit('new message', message);
            $mobile_textarea.val('')
        }
    });

    // 无限滚动
    var page = 1;
    var insertFlag=false;
    function load_messages(){
        var $messages = $('.messages');
        var position = $messages.scrollTop();
        if (position === 0 && socket.nsp !== '/anonymous'){
            page++;
            $('.ui.loader').toggleClass('active');
            $.ajax({
                type: 'GET',
                url: messages_url,
                data: {page: page},
                success: function (data) {
                    var before_height = $messages[0].scrollHeight;
                    $(data).prependTo(".messages").hide().fadeIn(800);
                    var after_height = $messages[0].scrollHeight;
                    flask_moment_render_all();
                    $messages.scrollTop(after_height - before_height);
                    $('.ui.loader').toggleClass('active');
                    activateSemantics();
                    },
                error: function () {
                    if (insertFlag === false ){
                        $('.messages').before("<br><div class='ui aligned center aligned grid'>没有更早的消息了...</div>");
                        insertFlag = true;
                    }
                    $('.ui.loader').toggleClass('active');
                }
            });
        }
    }
    $('.messages').scroll(load_messages);

    // delete message
    $('.delete-button').on('click', function () {
        var $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                $this.parent().parent().parent().remove();
            },
            error: function () {
                alert('Oops, something was wrong!');
            }
        });
    });

    //delete user
    $(document).on('click', '.delete-user-btn', function () {
        var $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                alert('Success, this user is gone!');
            },
            error: function () {
                alert('Oops, something was wrong!');
            }
        });
    });

    //quote message
    $('.quote-button').on('click', function () {
        var $textarea = $('#message-textarea');
        var message = $(this).parent().parent().parent().find('.message-body').text();
        $textarea.val('> ' + message + '\n\n');
        $textarea.val($textarea.val()).focus();
    });

    socket.on('user count', function (data) {
        $('#user-count').html(data.count);
    });

    // 产生桌面通知
    function messageNotify(data){
        if (Notification.permission !== "granted"){
            Notification.requestPermission();
        }else {
            var notification = new Notification('Message from' + data.nickname, {
                icon: data.gravatar,
                body: data.message_body.replace(/(<([^>]+)>)/ig, '')
            });

            notification.onclick = function () {
               window.open(root_url);
            };

            setTimeout(function () {
                notification.close();
            }, 4000);
        }
    }

    socket.on('new message', function (data) {
        message_count++;
        if (!document.hasFocus()){
            document.title = '(' + message_count + ')' + 'CatChat';
        }
        if (data.user_id !== current_user_id){
            messageNotify(data);
        }
        $('.messages').append(data.message_html);
        flask_moment_render_all();
        scrollToBottom();
        activateSemantics();
    });

    $(window).focus(function () {
        message_count = 0;
        document.title = 'CatChat';
    });

    document.addEventListener('DOMContentLoaded', function () {
        if(!Notification){
            alert('Desktop notifications not available in your browser.');
        }
        if (Notification.permission !== "granted"){
            Notification.requestPermission();
        }
    });
    scrollToBottom();
});