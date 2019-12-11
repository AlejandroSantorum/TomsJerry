$( function () {
    var next=true, prev=false, pause=true, interval_id;

    function nextMove(csfrVal) {
        csfrVal = $('[name=csrfmiddlewaretoken]').attr('value');
        if (next){
            $.ajax({
                type: 'POST',
                url: "/mouse_cat/get_move",
                data: {
                    'shift': 1,
                    'csrfmiddlewaretoken': csfrVal
                },
                success: function (result) {
                    og = result.origin;
                    tg = result.target;
                    next = result.next;
                    prev = result.previous


                    token = $('#cell_'+og).children()[0];
                    $('#cell_'+og).children().remove();
                    $('#cell_'+tg).html(token);
                    $('[name=next]').attr('disabled', !next);
                    $('[name=prev]').attr('disabled', !prev);
                }
            });
        } else {
            pause = true;
            $('[name=play-pause]').html("▶️");
            clearInterval(interval_id);
            alert($('#game-finished').attr('value') + ' won the game!');
        }
    };

    $('[name=next]').click(
        function () {
            csfrVal = $('[name=csrfmiddlewaretoken]').attr('value');
            nextMove(csfrVal);
        }
    );
    $('[name=prev]').click(
        function () {
            csfrVal = $('[name=csrfmiddlewaretoken]').attr('value');
            if (prev){
                $.ajax({
                    type: 'POST',
                    url: "/mouse_cat/get_move",
                    data: {
                        'shift': -1,
                        'csrfmiddlewaretoken': csfrVal
                    },
                    success: function (result) {
                        og = result.origin;
                        tg = result.target;
                        next = result.next;
                        prev = result.previous;


                        token = $('#cell_'+og).children()[0];
                        $('#cell_'+og).children().remove();
                        $('#cell_'+tg).html(token);
                        $('[name=next]').attr('disabled', !next);
                        $('[name=prev]').attr('disabled', !prev);
                    }
                });
            }
        }
    );

    $('[name=play-pause]').click(
        function () {
            csfrVal = $('[name=csrfmiddlewaretoken]').attr('value');
            if (pause){
                pause = !pause;
                $(this).html("⏸️");
                interval_id = setInterval(nextMove, 2000);
            } else {
                pause = !pause;
                $(this).html("▶️");
                clearInterval(interval_id);
            }
        }
    );
});
