$( function () {
    var nItems = Math.floor(Number( (window.innerHeight - $('#select-header').height() ) / $('.game-aref').height()));
    var page = 0;
    var visibles, transparent;
    var nPages;
    setVisibles();
    showVisibles();

    function setVisibles() {
        visibles = [];
        transparent = [];
        cats = $('#cat-filter').is(':checked');
        mice = $('#mouse-filter').is(':checked');

        if (cats) {
            // $('.card-cat-game').addClass('d-flex').removeClass('d-none');
            $('.card-cat-game').each( function () {
                visibles.push($(this));
            });
        }else{
            $('.card-cat-game').each( function () {
                transparent.push($(this));
            });
        }

        if (mice) {
            // $('.card-cat-game').addClass('d-flex').removeClass('d-none');
            $('.card-mouse-game').each( function () {
                visibles.push($(this));
            });
        }else{
            $('.card-mouse-game').each( function () {
                transparent.push($(this));
            });
        }

        nPages = Math.ceil( Number(visibles.length / nItems) )

        if (nPages == 0){
            $('[name=next]').attr('disabled', true);
            $('[name=prev]').attr('disabled', true);
        } else {
            $('[name=next]').attr('disabled', false);
            $('[name=prev]').attr('disabled', false);
        }

        if (nPages - 1 == page) {
            $('[name=next]').attr('disabled', true);
        }
        $('[name=prev]').attr('disabled', true);
        page = 0;
        $('#page-number').html(page+1);
    }

    function showVisibles() {
        let vStart = nItems * page;
        let vEnd = Math.min(vStart + nItems, visibles.length)
        
        for (var i = vStart; i < vEnd; i++) {
            visibles[i].addClass('d-flex').removeClass('d-none');
        }

        for (var i = 0; i < vStart; i++) {
            visibles[i].addClass('d-none').removeClass('d-flex');
        }

        for (var i = vEnd; i < visibles.length; i++ ){

            visibles[i].addClass('d-none').removeClass('d-flex');
        }

        for (t of transparent) {
            $(t).addClass('d-none').removeClass('d-flex');
        }
    }

    function shiftPage(shift) {
        page += shift;
        if (nPages - 1 == page) {
            $('[name=next]').attr('disabled', true);
        } else {
            $('[name=next]').attr('disabled', false);
        }
        if (page == 0){
            $('[name=prev]').attr('disabled', true);
        } else {
            $('[name=prev]').attr('disabled', false);
        }
        $('#page-number').html(page+1);
    }

    $('#cat-filter').change( function (event) {
        setVisibles();
        showVisibles();
    });

    $('#mouse-filter').change( function (event) {
        setVisibles();
        showVisibles();
    });

    $('[name=prev]').click( function () {
        shiftPage(-1);
        showVisibles();
    });

    $('[name=next]').click( function () {
        shiftPage(1);
        showVisibles();
    });
});
