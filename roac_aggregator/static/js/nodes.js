$(function() {
    function Node(name, status_, updated_at) {
        var self = this;
        self.name = ko.observable(name);
        self.status_ = ko.observable(status_);
        self.updated_at = ko.observable(updated_at);

        self.status_text = ko.computed(function() {
            return JSON.stringify(self.status_(), undefined, 2);
        });

        self.formatted_updated_at = ko.computed(function() {
          if(self.updated_at()) {
            days    = self.updated_at().getDate();
            month   = self.updated_at().getMonth() + 1;
            year    = self.updated_at().getFullYear();
            seconds = self.updated_at().getSeconds();
            minutes = self.updated_at().getMinutes();
            hours   = self.updated_at().getHours();
            return year+"-"+month+"-"+days+ " " +hours+":"+minutes+":"+seconds
          }
          return "Not defined"
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
