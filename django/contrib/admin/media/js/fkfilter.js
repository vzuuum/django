(function($) {
    $.fn.fk_filter = function(verbose_name) {
        return this.each(function() {
            var excluded;;
            var j = 0;
            $(this).attr('size', 2); // Force a multi-row <select>
            $(this).find('option[value=""]').remove(); // Remove the '-----'

            // Create the wrappers
            var outerwrapper = $('<div />', {
                'class': 'selector selector-single'
            });
            $(this).wrap(outerwrapper);
            var innerwrapper = $('<div />', {
                'class': 'selector-available'
            });
            $(this).wrap(innerwrapper);

            // Creates Header
            var header = $('<h2 />', {
                'text': interpolate(gettext('Available %s'), [verbose_name])
            }).insertBefore(this);

            // Creates search bar
            var searchbar = $('<p />', {
                'html': '<img src="' + window.__admin_media_prefix__ + 'img/admin/selector-search.gif"> <input type="text" id="' + $(this).attr('id') + '_input">',
                'class': 'selector-filter'
            }).insertBefore(this);

            var select = $(this);
            var original = select.clone();

            var filter = $('#' + $(this).attr('id') + '_input');
            var excluded = [];
            var lastPatternLength = 0;

            filter.bind('keyup.fkfilter', function(evt) {
                /*
                Procedure for filtering options::

                    * Detach the select from the DOM so each change doesn't
                      trigger the browser to re-render.
                    * If the pattern is longer than the previous pattern, then
                      we can skip any excluded select options and search the
                      included options for pattern matches.
                    * If the pattern is shorter, then we're forced to check
                      excluded select options for matches.
                    * ``matched`` is incremented whenever an excluded select
                      option is matched so that we don't have to search
                      recently appended options twice.
                    * Note the length of the pattern in ``lastPatternLength``.
                    * Append the select back into the DOM for rendering.
                */
                var i, size, option, options;
                var pattern = filter.val();
                var parent = select.parent();
                var matched = 0;
                select.detach();
                if (lastPatternLength > pattern.length) {
                    size = excluded.length;
                    for (i = 0; i < size; i++) {
                        option = excluded[i];
                        if (option.text().indexOf(pattern) !== -1) {
                            select.append(option);
                            matched++;
                        }
                    }
                }
                options = select.children();
                size = options.length - matched;
                for(i = 0; i < size; i++) {
                    if (options[i].text.indexOf(pattern) === -1) {
                        option = $(options[i]).detach();
                        excluded.push(option);
                    }
                }
                lastPatternLength = pattern.length;
                parent.append(select);
            });
        });
    };
})(django.jQuery);

