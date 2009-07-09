dojo.require("dojox.data.QueryReadStore");
dojo.provide("custom.GetReadStore");
dojo.declare("custom.GetReadStore", dojox.data.QueryReadStore, {
	fetch:function(request) {
	    request.serverQuery = {q:request.query.name};
	    // Call superclasses' fetch
	    return this.inherited("fetch", arguments);
	}
    });