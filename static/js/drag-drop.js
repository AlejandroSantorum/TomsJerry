$( function() {
    $("[id^=cat-drag]").each(
        function () {
            $( this ).draggable(
                {revert: "invalid"}
            )
        }
    )

    $("[id^=mouse-drag]").each(
        function () {
            $( this ).draggable(
                {revert: "invalid"}
            )
        }
    )

    $("[id^=cell_]").each(
        function () {
            $( this ).droppable({
                drop: function (event, ui) {
                    $( this ).html(ui.draggable.removeAttr("style").prop('outerHTML'));
                    ui.draggable.remove();
                    $("[id^=cat-drag]").each(
                        function () {
                            $( this ).draggable(
                                {revert: "invalid"}
                            )
                        }
                    );
                    $("[id^=mouse-drag]").each(
                        function () {
                            $( this ).draggable(
                                {revert: "invalid"}
                            )
                        }
                    );
                }
            })
        }
    )

});
