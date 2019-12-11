$( function () {
    var nItems = Math.floor(Number( (window.innerHeight - $('#select-header').height() ) / $('.game-aref').height()));
    var page = 0;
    var visibles, transparent;
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

    }

    function showVisibles() {
        let vStart = nItems * page;
        let vEnd = Math.min(vStart + nItems, visibles.length)
        console.log(vStart, vEnd, visibles.length);
        for (var i = vStart; i < vEnd; i++) {
            visibles[i].addClass('d-flex').removeClass('d-none');
        }

        for (var i = 0; i < vStart; i++) {
            visibles[i].addClass('d-none').removeClass('d-flex');
        }

        for (var i = vEnd; i < visibles.length; i++ ){
            console.log('Deleting');
            visibles[i].addClass('d-none').removeClass('d-flex');
        }

        for (t of transparent) {
            $(t).addClass('d-none').removeClass('d-flex');
        }
    }

    $('#cat-filter').change( function (event) {
        setVisibles();
        showVisibles();
    });

    $('#mouse-filter').change( function (event) {
        setVisibles();
        showVisibles();
    });
});
