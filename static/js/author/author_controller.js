/**
 * Top level presenter / presentation logic to manage user / author controls.
 *
 * @author Rory Olsen (Gleap LLC, 2014)
 * @author Sam Pottinger (Gleap LLC, 2014)
**/

window.AuthorControlsView = Backbone.View.extend({

    tagName: 'div',

    initialize:function () {
        this.listingView = new ListingView({model: this.model});
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

    /**
     * Post-render event listener to attach jquery event handlers.
    **/
    // afterRender: function (){
    //     $('.author-view-tab a').click(function (e) {
    //         var tabName = $(e.target).attr('href');
    //         var targetParentJQuery = $(e.target).parent();

    //         $('.author-view-tab').removeClass('active');
    //         $('.tab-pane').removeClass('active');

    //         targetParentJQuery.addClass('active');
    //         $(tabName + '-tab').addClass('active');
    //         return false;
    //     });

    //     $('#individual-document-view').ready(function () {
    //         window.adjustHeights();
    //     });
    // }
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