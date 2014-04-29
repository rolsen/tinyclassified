/**
 * Model that represents a TinyClassified listing.
**/
window.Listing = Backbone.Model.extend({
    urlRoot: '/author/',
    defaults: {
        'author_email': null,
        'name': null,
        'about': '',
        'slugs': [],
        'tags': []
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
        // this.socialView = new ListingSocialView({model: this.model});
        // this.showcaseView = new ListingShowcaseView({model: this.model});
        this.nameView = new ListingNameView({model: this.model});
        this.aboutView = new ListingAboutView({model: this.model});
        this.model.bind('change', this.render, this);

        this.model.set({'_id' : '_current'});
        this.model.fetch();
    },

    render:tinyClassifiedUtil.getViewRender(),
    close:tinyClassifiedUtil.getViewClose(),

    afterRender:function () {
        tinyClassifiedUtil.assign(this.contactView, '#contacts-view');
        // tinyClassifiedUtil.assign(this.socialView, '#social-view-display');
        // tinyClassifiedUtil.assign(this.showcaseView, '#showcase-view-display');
        tinyClassifiedUtil.assign(this.nameView, '#name-view');
        tinyClassifiedUtil.assign(this.aboutView, '#about-view');
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
        this.model.save();
        return false;
    },

    render: tinyClassifiedUtil.getViewRender(),
    close: tinyClassifiedUtil.getViewClose()
});
