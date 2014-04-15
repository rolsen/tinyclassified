
window.ListingContact = Backbone.Model.extend({
    defaults:{
        'type': 'DEFAULTtype',
        'value': 'DEFAULTvalue'
    },
    idAttribute: "_id"
});

window.ListingContactCollection = Backbone.Collection.extend({
    url:'contact',
    model: ListingContact
});

window.ListingContactView = Backbone.View.extend({

    template:_.template($('#contacts-view-template').html()),

    initialize: function () {
        this.contactCollection = new ListingContactCollection();
        this.contactCollectionView = new ListingContactCollectionView({
            model: this.contactCollection
        });
        this.contactAddView = new ListingContactAddView();
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

window.ListingContactCollectionView = Backbone.View.extend({

    tagName:'table',

    className:'table table-striped',

    template:_.template($('#contact-table-template').html()),

    /**
     * Constructor for the contact list presenter.
    **/
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
    **/
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
        return false;
    },

    render:tinyClassifiedUtil.getViewRender(),
    close:tinyClassifiedUtil.getViewClose()
});

window.ListingContactAddView = Backbone.View.extend({

    template:_.template($('#add-contact-view-template').html()),

    events:{
        'click #add-contact-button':'newContact'
    },

    initialize:function () {
        this.render()
    },

    newContact:function () {
        // console.log("ListingContactAddView");
        // if (!$('#contact-add-form').parsley('validate')) {
        //     return;
        // }
        // console.log("ListingContactAddView post validate");

        var elem = $(this.el);
        var contact = new ListingContact();
        contact.set({
            'type': elem.find('#type-input').val(),
            'value': elem.find('#value-input').val()
        });
        result = this.contactCollection.create(contact, {wait: true});
        console.log('result = this.contactCollection.create(contact);');
        console.log(result);

        elem.find('#value-input').val('');
        return false;
    },

    render:function () {
        $(this.el).html(this.template());
        return this;
    },

    close:tinyClassifiedUtil.getViewClose()
});