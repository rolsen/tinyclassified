/**
 * @fileoverview Utility functions for client-side tasks.
 * @author rory@gleap.org (Rory Olsen)
 * @author sam@gleap.org (Sam Pottinger)
 * @license GNU GPLv3
 */

var tinyClassifiedUtil = {
    /**
     * Delegate a subsection of the view to another presenter.
     * @param {Backbone.View} view The presenter to assign.
     * @param {String} selector The jquery selector for the element to assign
     *      the presenter to (the element to delegate the presenter to).
     */
    assign:function (view, selector) {
        view.setElement($(selector)).render();
    },

    flashUser: function () {
        $('#flash-bar').stop().slideUp().slideDown().delay(3000).slideUp();
    },

    getUrlVars: function () {
        var vars = [], hash;
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
        for(var i = 0; i < hashes.length; i++)
        {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = hash[1];
        }
        return vars;
    },

    /**
     * Default clean up of a Backbone.View. Calls beforeClose() if it exists.
     */
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
     */
    getViewRender:function() {
        return function () {
            $(this.el).html(this.template(this.model.toJSON()));
            if (this.afterRender) {
                this.afterRender();
            }

            return this;
        };
    }
};