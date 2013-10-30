$(function() {
    function NodesModel() {
        var self = this;
        self.nodes = ko.observableArray([]);
        self.selected_node = ko.observable();
        self.node = ko.observable();

        self.update_nodes = function() {
            $.getJSON("/api/v1/nodes", function(data) {
                var nodes = $.map(data, function(n) {
                    return new NodeLink(n.name, n.url);
                });
                self.nodes(nodes);
                self.switch_node(self.nodes()[0])
            });
        };

        self.switch_node = function(node) {
            self.selected_node(node)
            $.getJSON(node.url(), function(data) {
              var updated_at = Date.parse(data["updated_at"]);
              if(updated_at) {
                updated_at = new Date(updated_at);
              }
              var node = new Node(data.name, data.status, updated_at);
              self.node(node);
            });
        };

        self.update_node = function() {
            self.switch_node(self.selected_node());
        };

        self.update_nodes()
    }

    ko.applyBindings(new NodesModel());
});
