
(function () {

    var nextPage;

    getUserOfferings = function getUserOfferings (target, callback, count) {

        var filter, offeringsPage;

        offeringsPage = $('#number-offerings').val();

        if (target == '#provided-tab') {
            filter = '?filter=provider&state=all';
        } else if (target == '#purchased-tab'){
            filter = '?filter=purchased';
        }
        if (count) {
            filter += '&action=count'
        } else {
            // Set number of offerings per page
            filter += '&limit=' + offeringsPage;
            // Set the first element
            filter += '&start=' + ((offeringsPage * (nextPage - 1)) + 1);
        }
        $.ajax({
            type: "GET",
            url: EndpointManager.getEndpoint('OFFERING_COLLECTION') + filter,
            dataType: 'json',
            success: function(response) {
                callback(target, response);
            },
            error: function(xhr) {
                var msg = 'Error the server responds with code ' + xhr.status;
                MessageManager.showMessage('Error', msg);
            }

        })
    }

    paintProvidedOfferings = function paintProvidedOfferings (target, data) {

        $(target).empty();
        for (var i = 0; i < data.length; i++) {
            var offering_elem = new OfferingElement(data[i]);

            $.template('miniOfferingTemplate', $('#mini_offering_template'));
            $.tmpl('miniOfferingTemplate', {
                'name': offering_elem.getName(),
                'organization': offering_elem.getOrganization(),
                'logo': offering_elem.getLogo(),
                'state': offering_elem.getState(),
                'rating': offering_elem.getRating(),
                'description': offering_elem.getShortDescription()
            }).appendTo(target).click(paintOfferingDetails.bind(this, offering_elem, paintCatalogue, '#catalogue-container'));
        }
    };

    setNextPage = function setNextPage (nextPag) {
        nextPage = nextPag;
    };

})();
