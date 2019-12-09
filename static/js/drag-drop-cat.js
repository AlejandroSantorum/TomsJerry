

$( function() {
    function targetPos(x, y, inc_x, inc_y) {
        tg_x = x + inc_x;
        tg_y = y + inc_y;
        if (tg_x < 0 || tg_x > 7 || tg_y < 0 || tg_y > 7) {
            return undefined;
        }
        return tg_x + tg_y*8;
    }

    function dropAction(event, ui){
        // Refresh UI
        $(this).html(ui.draggable.removeAttr("style").prop('outerHTML'));
        origin = ui.draggable.parent().attr('id').split('_')[1];
        target = $(this).attr('id').split('_')[1];
        ui.draggable.remove();
        $("[id^=cat-drag]").draggable(
                {
                    revert: "invalid",
                    start: calcDrop,
                    stop: removeDrop
                }
            );

        //Send AJAX petition
        csfrVal = $('[name=csrfmiddlewaretoken]').attr('value');
        $.ajax({
            type: 'POST',
            url: "/mouse_cat/move",
            data: {
                'origin': origin,
                'target': target,
                'csrfmiddlewaretoken': csfrVal
                },
            success: function () {
                $('#content-div').load('/mouse_cat/show_game');
            }
            });
    }

    function calcDrop(event, ui) {
        // Calculations
        origin = $(this).parent().attr('id').split('_')[1];
        type = $(this).attr('id').split('-')[0];
        og_x = Number(origin) % 8;
        og_y = Math.floor(Number(origin)/8);
        possible_moves = [];
        possible_moves[0] = targetPos(og_x, og_y, 1, 1);
        possible_moves[1] = targetPos(og_x, og_y, -1, 1);
        if (type == 'mouse'){
            possible_moves[2] = targetPos(og_x, og_y, -1, -1);
            possible_moves[3] = targetPos(og_x, og_y, 1, -1);
        }

        // Initialise droppables
        for (target of possible_moves) {
            if (target) {
                if ($('#cell_'+target).children().length == 0){
                    $('#cell_'+target).addClass('light-cell');
                    $('#cell_'+target).droppable({
                        drop: dropAction
                    })
                }
            }
        }
    }

    function removeDrop(event, ui){
        $(".light-cell").each(
            function () {
                console.log(this);
                $(this).removeClass('light-cell');
                $(this).droppable('destroy');
            }
        )
    }

    // INITIALIZATIONS
    $("[id^=cat-drag]").draggable(
            {
                revert: "invalid",
                start: calcDrop,
                stop: removeDrop
            }
        );
});
