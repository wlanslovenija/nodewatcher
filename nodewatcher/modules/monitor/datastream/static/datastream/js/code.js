(function ($) {
    $(document).ready(function () {
        var $nodeGraphs = $('.node-graphs');
        $nodeGraphs.datastream({
            'streamListUri': $nodeGraphs.data('source'),
            'streamListParams': {
                'tags__visualization__initial_set': true,
                'tags__node': $nodeGraphs.data('node'),
                // More streams per page.
                'limit': 500
            }
        });
    });
})(jQuery);
