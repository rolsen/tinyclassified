// TODO: Remove dead code here.


/**
 * Top level presenter / presentation logic to manage user / author controls.
 * @author rory@gleap.org (Rory Olsen)
 * @author sam@gleap.org (Sam Pottinger)
 * @license GNU GPLv3
 */
window.AuthorControlsView = Backbone.View.extend({

    tagName: 'div',

    initialize:function () {
        console.log('starting');
        this.listingView = new ListingView({model: this.model});

        // TODO:
        // this.jobPostingsView = new JobPostingsView({model: this.model});
        // this.premiumFeaturesView = new PremiumFeaturesView({model: this.model});

        this.model.bind('change', this.render, this);
        this.render();
    },

    render: function () {
        $(this.el).html(this.template(this.model.toJSON()));
        console.log("HEHEHERE")
        if (this.afterRender) {
            this.afterRender();
        }

        return this;
    },

    close:tinyClassifiedUtil.getViewClose(),

    afterRender:function () {
        tinyClassifiedUtil.assign(this.listingView, '#listing-tab');
        $.getJSON(
            './categories.json',
            function (categoriesInfo) {
                var categories = [];
                for (category in categoriesInfo)
                    categories.push(category);

                $('#category').autocomplete({
                    source: category
                });
            }
        )
    }
});

// Router
var AppRouter = Backbone.Router.extend({

    routes: {
        '':'authorControls',
        'listing':'authorControls'
    },

    authorControls:function () {
        this.listing = new Listing();
        this.listingView = new ListingView({model: this.listing});
        this.listing.fetch();

        tinyClassifiedUtil.assign(this.listingView, '#listing-details-tab');
        return false;
    },

});

var app = new AppRouter();
Backbone.emulateJSON = true;
Backbone.history.start();