function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}


/**
 * Model that represents a TinyClassified listing.
**/
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
        }
    },
    idAttribute: "_id"
});

/**
 * Presenter to show controls to edit and view a listing.
**/
window.ListingView = Backbone.View.extend({

    template:_.template($('#listing-details-template').html()),

    initialize:function () {
        this.contactView = new ListingContactView({model: this.model});
        this.nameView = new ListingNameView({model: this.model});
        this.tagsView = new ListingTagsView({model: this.model});
        this.aboutView = new ListingAboutView({model: this.model});
        this.addressView = new ListingAddressView({model: this.model});

        var targetID = getUrlVars()['target'];
        if (targetID)
            targetID = decodeURIComponent(targetID);
        else
            targetID = '_current';

        this.model.bind('change', this.render, this);
        this.model.set({'_id' : targetID});
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
    },

    beforeClose:function () {
        if (this.contactView) {
            this.contactView.close();
        }
    }
});

window.ListingNameView = Backbone.View.extend({

    template:_.template($('#listing-name-template').html()),

    events:{
        'click #save-name-button': 'saveName'
    },

    saveName:function () {
        this.model.set({
            name: $(this.el).find('#listing-name').val()
        });
        tinyClassifiedUtil.flashUser();
        this.model.save();
        return false;
    },

    render: tinyClassifiedUtil.getViewRender(),
    close: tinyClassifiedUtil.getViewClose()
});

window.ListingTagsView = Backbone.View.extend({

    template:_.template($('#listing-tags-template').html()),

    events:{
        'click #add-tag-button': 'addSubcategory'
    },

    debugLogTags: function (tags) {
        _.each(
            tags,
            function(value, key, list) {
                console.log(value);
                _.each(
                    list[key],
                    function(subcat) {
                        console.log(subcat);
                    }
                );
                console.log("delim");
            }
        );
    },

    renderTagsList: function () {
        var template = _.template($('#listing-tags-listing-template').html());
        var tags = dict(this.model.attributes.tags);
        var rows = [];
        tags.forEach(function (subtags, cat_output) {
            rows.push.apply(rows, subtags.map(function (subtag) {
                return template({cat_output: cat_output.replace('_slash_', '/'), subtag: subtag});
            }));
        });
        $('#tags-list').html(rows.join('\n'));
    },

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