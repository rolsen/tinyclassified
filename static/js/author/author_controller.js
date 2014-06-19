/**
 * Top level presenter / presentation logic to manage user / author controls.
 * @author rory@gleap.org (Rory Olsen)
 * @author sam@gleap.org (Sam Pottinger)
 * @license GNU GPLv3
 */
window.AuthorControlsView = Backbone.View.extend({

    tagName: 'div',

    initialize:function () {
        this.listingView = new ListingView({model: this.model});

        // TODO:
        // this.jobPostingsView = new JobPostingsView({model: this.model});
        // this.premiumFeaturesView = new PremiumFeaturesView({model: this.model});

        this.model.bind('change', this.render, this);
        this.render();
    },

    render:tinyClassifiedUtil.getViewRender(),
    close:tinyClassifiedUtil.getViewClose(),

    afterRender:function () {
        tinyClassifiedUtil.assign(this.listingView, '#listing-tab');
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