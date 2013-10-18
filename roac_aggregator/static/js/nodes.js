$(function() {
  function NodesModel() {
    var self = this;
    self.nodes = ko.observableArray([]);
    self.active_node = ko.observable();
    
    self.update_nodes = function() {
      $.getJSON("/api/v1/nodes", function(data) {
        self.nodes(data);
        self.change_node(self.nodes()[0])
      });
    };

    self change_node = function(node) {
      self.active_node(node)
    };

    self.update_nodes()
  }
  ko.applyBindings(new NodesModel());
});
