/**
 * @fileoverview Contains the models/views associated with a listing about section.
 * @author rory@gleap.org (Rory Olsen)
 * @author sam@gleap.org (Sam Pottinger)
 * @license GNU GPLv3
 */

 /**
  * Model that represents a listing contact.
  */
window.ListingContact = Backbone.Model.extend({
    defaults:{
        'type': '',
        'value': '',
        'parent': '_current'
    },
    idAttribute: "_id"
});

window.ListingContactCollection = Backbone.Collection.extend({
    url:'content/contact',
    model: ListingContact
});

/**
 * Presenter / manager to coordinate presentation of a contact collection and
 *     creation.
 */
window.ListingContactView = Backbone.View.extend({

    template:_.template($('#contacts-view-template').html()),

    initialize: function () {
        var ListingContactCollection = Backbone.Collection.extend({
            url: 'content/' + encodeURIComponent(this.model.attributes.author_email) + '/contact',
            model: ListingContact
        });
        this.contactCollection = new ListingContactCollection();
        this.contactCollection.parent = this.model;
        this.contactCollectionView = new ListingContactCollectionView({
            model: this.contactCollection
        });
        this.contactAddView = new ListingContactAddView({
            model: this.model
        });
        this.contactAddView.contactCollection = this.contactCollection;

        this.contactCollection.fetch();
    },

    beforeClose: function () {
        if (this.contactCollectionView) { this.contactCollectionView.close(); }
        if (this.contactAddView) { this.contactAddView.close(); }
    },

    render:tinyClassifiedUtil.getViewRender(),

    afterRender: function () {
        tinyClassifiedUtil.assign(this.contactCollectionView, '#contact-collection-view');
        tinyClassifiedUtil.assign(this.contactAddView, '#contact-add-view');
    },

    close:tinyClassifiedUtil.getViewClose()
});

/**
 * Presenter to display the controls to edit and view many listing contacts.
 */
window.ListingContactCollectionView = Backbone.View.extend({

    tagName:'table',

    className:'table table-striped',

    template:_.template($('#contact-table-template').html()),

    /**
     * Constructor for the contact list presenter.
     */
    initialize: function () {
        this.model.bind('reset', this.render, this);
        var self = this;
        this.model.bind('add', function (contact) {
            $(self.el).append(
                new ListingContactCollectionItemView({model:contact}).render().el
            );
        });
    },

    /**
     * Generate the HTML view for the collection of contacts.
     */
    render: function (eventName) {
        $(this.el).html(this.template());
        _.each(this.model.models, function (contact) {
            $(this.el).find('tbody').append(
                new ListingContactCollectionItemView({model:contact}).render().el
            );
        }, this);
        return this;
    },

    close:tinyClassifiedUtil.getViewClose()
});

/**
 * Presenter to display controls to edit and view a listing contact.
 */
window.ListingContactCollectionItemView = Backbone.View.extend({

    tagName:'tr',

    template:_.template($('#contact-item-template').html()),

    events:{
        'click #delete-contact-link':'deleteContact'
    },

    initialize:function () {
        this.model.bind('change', this.render, this);
        this.model.bind('destroy', this.close, this);
    },

    deleteContact:function () {
        this.model.destroy();
        tinyClassifiedUtil.flashUser();
        return false;
    },

    render:tinyClassifiedUtil.getViewRender(),
    close:tinyClassifiedUtil.getViewClose()
});

/**
 * Presenter to display the controls to add a new listing contact.
 */
window.ListingContactAddView = Backbone.View.extend({

    template:_.template($('#add-contact-view-template').html()),

    events:{
        'click #add-contact-button':'newContact'
    },

    initialize:function () {
        this.render()
    },

    newContact:function () {
        // TODO: Validate input
        // if (!$('#contact-add-form').parsley('validate')) {
        //     return;
        // }

        var elem = $(this.el);
        var contact = new ListingContact();
        contact.set({
            'type': elem.find('#type-input').val(),
            'value': elem.find('#value-input').val(),
            'parent': this.model.attributes.author_email
        });
        result = this.contactCollection.create(contact);

        elem.find('#value-input').val('');
        tinyClassifiedUtil.flashUser();
        return false;
    },

    render:function () {
        $(this.el).html(this.template());
        return this;
    },

    close:tinyClassifiedUtil.getViewClose()
});