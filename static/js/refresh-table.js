$( function () {


    reload();

    function reload() {
        console.log('hi');
        $('#chess_board').load('/mouse_cat/show_game #chess_board', function () {
            $('#user-turn').load('/mouse_cat/show_game #user-turn');
            console.log('settingTimeout');
            user = $('#draggable').html()

            $("[id^="+user+"-drag]").draggable(
                    {
                        revert: "invalid",
                        start: calcDrop,
                        stop: removeDrop
                    }
                );
            setTimeout(reload, 1000);
        });
    };

});
