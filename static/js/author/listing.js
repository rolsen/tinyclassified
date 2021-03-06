/**
 * @fileoverview The main listing model plus views. Relies on other listing
 * models and views.
 * @author rory@gleap.org (Rory Olsen)
 * @author sam@gleap.org (Sam Pottinger)
 * @license GNU GPLv3
 */

/**
 * Model that represents a TinyClassified listing.
 */
window.Listing = Backbone.Model.extend({
    urlRoot: '/resources/author/content/',
    defaults: {
        'author_email': null,
        'name': null,
        'about': '',
        'slugs': [],
        'tags': [],
        'address': {
            'address': '',
            'street': '',
            'street2': '',
            'city': '',
            'state': '',
            'zip': '',
            'country': '',
        },
        'featured': false,
        'thumbnail_url': ''
    },
    idAttribute: "_id"
});

/**
 * Presenter to show controls to edit and view a listing.
 */
window.ListingView = Backbone.View.extend({

    template:_.template($('#listing-details-template').html()),

    initialize:function () {
        var targetID = tinyClassifiedUtil.getUrlVars()['target'];
        if (targetID)
            targetID = decodeURIComponent(targetID);
        else
            targetID = '_current';
        this.model.set({'_id' : targetID});
        this.model.set({'author_email' : targetID});

        this.contactView = new ListingContactView({model: this.model});
        this.nameView = new ListingNameView({model: this.model});
        this.tagsView = new ListingTagsView({model: this.model});
        this.aboutView = new ListingAboutView({model: this.model});
        this.addressView = new ListingAddressView({model: this.model});

        this.model.bind('change', this.render, this);
        this.model.fetch();
    },

    render:tinyClassifiedUtil.getViewRender(),
    close:tinyClassifiedUtil.getViewClose(),

    afterRender:function () {
        tinyClassifiedUtil.assign(this.contactView, '#contacts-view');
        tinyClassifiedUtil.assign(this.nameView, '#name-view');
        tinyClassifiedUtil.assign(this.tagsView, '#tags-view');
        tinyClassifiedUtil.assign(this.aboutView, '#about-view');
        tinyClassifiedUtil.assign(this.addressView, '#address-view');

        console.log('here');
        $.getJSON(
            '/resources/author/categories.json',
            function (categoriesInfo) {
                var categories = [];
                for (category in categoriesInfo)
                    categories.push(category.replace('_slash_', '/'));

                $('#category').autocomplete({
                    source: categories
                });

                $('#category').blur(function () {
                    var category = $('#category').val();
                    $('#subcategory').autocomplete({
                        source: categoriesInfo[category.replace('/', '_slash_')]
                    });
                });
            }
        )
    },

    beforeClose:function () {
        if (this.contactView) {
            this.contactView.close();
        }
    }
});

/**
 * Presenter to show controls to edit and view a listing name.
 */
window.ListingNameView = Backbone.View.extend({

    template:_.template($('#listing-name-template').html()),

    events:{
        'click #save-name-button': 'saveName'
    },

    saveName:function () {
        // TODO: This both saves the name and the featured status
        this.model.set({
            name: $(this.el).find('#listing-name').val(),
            featured: $(this.el).find('#featured-check').is(':checked'),
            thumbnail_url: $(this.el).find('#thumbnail-url-entry').val()
        });
        tinyClassifiedUtil.flashUser();
        this.model.save();
        return false;
    },

    render: tinyClassifiedUtil.getViewRender(),
    close: tinyClassifiedUtil.getViewClose()
});

/**
 * Presenter to show controls to edit and view a listing's tags.
 */
window.ListingTagsView = Backbone.View.extend({

    template:_.template($('#listing-tags-template').html()),

    events:{
        'click #add-tag-button': 'addSubcategory'
    },

    /**
     * Update the view, based on the model.
     */
    renderTagsList: function () {
        var template = _.template($('#listing-tags-listing-template').html());
        var tags = dict(this.model.attributes.tags);
        var rows = [];
        tags.forEach(function (subtags, cat_output) {
            rows.push.apply(rows, subtags.map(function (subtag) {
                return template({
                    cat_output: cat_output.replace('_slash_', '/'),
                    subtag: subtag
                });
            }));
        });
        $('#tags-list').html(rows.join('\n'));
    },

    /**
     * Fetch tag information and add it to the model.
     */
    addSubcategory: function () {
        var category = $('#category').val();
        var subcategory = $('#subcategory').val();

        var tags = dict(this.model.get('tags'));

        if (!tags.has(category))
            tags.set(category, []);

        tags.get(category).push(subcategory);
        this.model.set('tags', dictAsObj(tags));
        tinyClassifiedUtil.flashUser();
        this.model.save();
        return false;
    },

    /**
     * Delete a subcategory from a tags obj.
     * @param {Object} tags The tags object to modify.
     * @param {String} cat_output The url-safe category to which subtag belogs to.
     * @param {String} subtag The subcategory to remove.
     * @return {Object} The tags input minus the removed subtag.
     */
    deleteSubcategory: function (tags, cat_output, subtag) {
        tags = dict(tags);
        var category = tags.get(cat_output);
        category = _.without(category, subtag);

        if (category.length == 0)
            tags.delete(cat_output);
        else
            tags.set(cat_output, category);

        return dictAsObj(tags);
    },

    render: tinyClassifiedUtil.getViewRender(),

    /**
     * Fetch tag information, delete it from the model, and update the view.
     * @param {jQuery.Event} event The delete-triggering event, which must have
     *     a target element containing the tag information to be deleted.
     */
    handleDeleteTag: function (event) {
        event.preventDefault();
        var cat_output = $(event.target).attr('cat_output');
        var subtag = $(event.target).attr('subtag');

        var tags = this.model.get('tags');
        cat_output = cat_output.replace('/', '_slash_');
        tags = this.deleteSubcategory(tags, cat_output, subtag);
        this.model.set('tags', tags);

        this.renderTagsList();

        tinyClassifiedUtil.flashUser();
        this.model.save();
        return false;
    },

    afterRender: function () {
        this.renderTagsList();

        var self = this;
        var callback = function(event) {
            self.handleDeleteTag(event);
        };

        $('.delete-tag-link').click(callback);
    },

    close: tinyClassifiedUtil.getViewClose()
});

/**
 * Presenter to show controls to edit and view a listing address.
 */
window.ListingAddressView = Backbone.View.extend({

    template:_.template($('#listing-address-template').html()),

    events:{
        'click #save-address-button': 'saveAddress'
    },

    saveAddress:function () {
        this.model.set({
            address: {
                address: $(this.el).find('#address-input').val(),
                street: $(this.el).find('#street-input').val(),
                street2: $(this.el).find('#street2-input').val(),
                city: $(this.el).find('#city-input').val(),
                state: $(this.el).find('#state-input').val(),
                zip: $(this.el).find('#zip-input').val(),
                country: $(this.el).find('#country-input').val(),
            }
        });

        tinyClassifiedUtil.flashUser();
        this.model.save();
        return false;
    },

    render: tinyClassifiedUtil.getViewRender(),
    close: tinyClassifiedUtil.getViewClose()
});