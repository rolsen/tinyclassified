

// /**
//  * Presenter / backbone view for the document general properties tab.
// **/
window.ListingAboutView = Backbone.View.extend({
// window.DocumentPropertiesView = Backbone.View.extend({

    template:_.template($('about-view-template').html()),
//     template:_.template($('#doc-properties-template').html()),

    events:{
        'click #save-about-button': 'saveAbout'
    },
//     events:{
//         'click #save-doc-button': 'saveDocument',
//         'click #delete-doc-button': 'deleteDocument',
//         'click .feature-option-check': 'onFeatureOptionCheck',
//         'click .list-option-check': 'onListOptionCheck'
//     },

    render:function () {
        if (tinyMCE.activeEditor) {
            tinyMCE.activeEditor.remove();
        }

        $(this.el).html(this.template(this.model.toJSON()));
    //     window.requestedId = this.model.id;
    //     $('#doc-item-' + this.model.id).addClass('selected');

        var self = this;
        var render = function () {self.afterRender(self); };
        _(render).defer();

        return this;
    },
    // render:function (eventName) {
    //     if (tinyMCE.activeEditor)
    //         tinyMCE.activeEditor.remove();

    //     $(this.el).html(this.template(this.model.toJSON()));
    //     window.requestedId = this.model.id;
    //     $('#doc-item-' + this.model.id).addClass('selected');

    //     var self = this;
    //     var render = function () { self.afterRender(self); };
    //     _(render).defer();

    //     return this;
    // },

    afterRender: function (self) {
        tinymce.init({selector: "textarea.mceEditor"});
    },
//     afterRender: function (self) {
        // deleted stuff about pickings dates
//     },

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
        window.displayConfirmation('Saved.');

        return false;
    }
//     saveDocument:function () {

//         this.model.set({
//             title: $('#title').val(),
//             company: $('#company').val(),
//             short_summary: reMarker.render(tinyMCE.activeEditor.getContent())
//         });

//         if (this.model.isNew()) {
//             app.documentList.create(this.model);
//             window.displayConfirmation('Document created.');
//         } else {
//             this.model.save();
//             window.displayConfirmation('Document saved.');
//         }

//         return false;
//     },

//     /**
//      * Delete the current document along with resources and all.
//     **/
//     deleteDocument:function () {
//         // TODO: Confirm dialog
//         this.model.destroy({
//             success:function () {
//                 window.history.back();
//             }
//         });

//         app.navigate(
//             '',
//             {trigger: true}
//         );

//         return false;
//     },

//     /**
//      * Deactivate and empty all of the document general properties tab.
//     **/
//     close:function () {
//         $(this.el).unbind();
//         $(this.el).empty();
//     },

//     /**
//      * Event handler for when the feature until date / option is changed.
//      *
//      * Event handler for when the feature until option (don't, indefinitely,
//      * until date) is changed.
//     **/
//     onFeatureOptionCheck: function () {
//         var checked = $('#feature-duration-check').is(':checked');

//         if (checked) {
//             $('#feature-date-selector-holder').slideDown();
//         } else  {
//             $('#feature-date-selector-holder').slideUp();
//         }
//     },

//     /**
//      * Event handler for when the list until date / option is changed.
//      *
//      * Event handler for when the list until option (don't, indefinitely, until
//      * date) is changed.
//     **/
//     onListOptionCheck: function () {
//         var checked = $('#list-duration-check').is(':checked');

//         if (checked) {
//             $('#list-date-selector-holder').slideDown();
//         } else  {
//             $('#list-date-selector-holder').slideUp();
//         }
//     }
});
