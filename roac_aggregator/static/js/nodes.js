$(function() {
    function Node(name, status_) {
        var self = this;
        self.name = ko.observable(name);
        self.status_ = ko.observable(status_);
        self.status_text = ko.computed(function() {
            return JSON.stringify(self.status_(), undefined, 2);
        });
    }

    function NodesModel() {
        var self = this;
        self.nodes = ko.observableArray([]);
        self.selected_node = ko.observable();
        self.node = ko.observable();

        self.update_nodes = function() {
            $.getJSON("/api/v1/nodes", function(data) {
                self.nodes(data);
                self.switch_node(self.nodes()[0])
            });
        };

        self.switch_node = function(node) {
            self.selected_node(node)
            $.getJSON("/api/v1/nodes/" + node, function(data) {
                var node = new Node(data["name"], data["status"]);
                self.node(node);
                console.log(node.status_text());
            });
        };

        self.update_node = function() {
            self.switch_node(self.selected_node());
        };

        self.update_nodes()
    }

    ko.applyBindings(new NodesModel());
});
