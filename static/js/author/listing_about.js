
// /**
//  * Presenter / backbone view for the About Me.
// **/
window.ListingAboutView = Backbone.View.extend({

    template:_.template($('#about-view-template').html()),

    events:{
        'click #save-listing-button': 'saveAbout'
    },

    render:function () {
        if (tinyMCE.activeEditor) {
            tinyMCE.activeEditor.remove();
        }

        $(this.el).html(this.template(this.model.toJSON()));

        var self = this;
        var render = function () {self.afterRender(self); };
        _(render).defer();

        return this;
    },

    afterRender: function (self) {
        tinymce.init({selector: "textarea.mceEditor"});
    },

    saveAbout: function () {
        // if (!$('#about-form').parsley('validate')) {
        //     return;
        // }

        var options = {
            link_list:  false,    // render links as references, create link list as appendix
            h1_setext:  true,     // underline h1 headers
            h2_setext:  true,     // underline h2 headers
            h_atx_suf:  false,    // header suffixes (###)
            gfm_code:   false,    // gfm code blocks (```)
            li_bullet:  "*",      // list item bullet style
            hr_char:    "-",      // hr style
            indnt_str:  "    ",   // indentation string
            bold_char:  "*",      // char used for strong
            emph_char:  "_",      // char used for em
            gfm_del:    true,     // ~~strikeout~~ for <del>strikeout</del>
            gfm_tbls:   true,     // markdown-extra tables
            tbl_edges:  false,    // show side edges on tables
            hash_lnks:  false,    // anchors w/hash hrefs as links
            br_only:    false,    // avoid using "  " as line break indicator
            col_pre:    "col ",   // column prefix to use when creating missing headers for tables
            unsup_tags: {         // handling of unsupported tags, defined in terms of desired output style. if not listed, output = outerHTML
                // no output
                ignore: "script style noscript",
                // eg: "<tag>some content</tag>"
                inline: "span sup sub i u b center big",
                // eg: "\n\n<tag>\n\tsome content\n</tag>"
                block2: "div form fieldset dl header footer address article aside figure hgroup section",
                // eg: "\n<tag>some content</tag>"
                block1c: "dt dd caption legend figcaption output",
                // eg: "\n\n<tag>some content</tag>"
                block2c: "canvas audio video iframe",
            },
        };

        var reMarker = new reMarked(options);
        this.model.set({
            about: reMarker.render(tinyMCE.activeEditor.getContent())
        });

        this.model.save();
        tinyClassifiedUtil.flashUser();
        return false;
    }
});
