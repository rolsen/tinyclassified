/**
 * Utility functions for client-side tasks.
 *
 * @author: Rory Olsen (rolsen, Gleap LLC 2014)
**/

var tinyClassifiedUtil = {
    /**
     * Delegate a subsection of the view to another presenter.
     *
     * @param {Backbone.View} view The presenter to assign.
     * @param {String} selector The jquery selector for the element to assign
     *      the presenter to (the element to delegate the presenter to).
    **/
    assign:function (view, selector) {
        view.setElement($(selector)).render();
    },

    flashUser: function () {
        $('#flash-bar').slideDown().delay(3000).slideUp();
    },

    /**
     * Default clean up of a Backbone.View. Calls beforeClose() if it exists.
    **/
    getViewClose:function() {
        return function () {
            if (this.beforeClose) {
                this.beforeClose();
            }
            this.remove();
            this.unbind();
        };
    },

    /**
     * Default rendering of a Backbone.View. Calls afterRender if it exists.
    **/
    getViewRender:function() {
        return function () {
            // if (typeof this.currentlyRendered !== 'undefined') {
            //     this.close();
            // }

            $(this.el).html(this.template(this.model.toJSON()));
            if (this.afterRender) {
                this.afterRender();
            }
            // this.currentlyRendered = true;
            return this;
        };
    }
};