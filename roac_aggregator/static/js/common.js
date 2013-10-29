ko.bindingHandlers.highlight = {
    init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
      if(ko.unwrap(valueAccessor)) {
        hljs.highlightBlock(element);
      }
    },
    update: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
      if(ko.unwrap(valueAccessor)) {
        hljs.highlightBlock(element);
      }
    }
}

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

function Record(name, created_at, results) {
  var self = this;
  self.name = ko.observable(name);
  self.created_at = ko.observable(created_at);
  self.results = ko.observableArray(results);

  self.formated_date = ko.computed(function() {
    date = self.created_at().getDate();
    month = self.created_at().getMonth() + 1;
    year = self.created_at().getFullYear();
    return year + '-' + month + '-' + date;
  });

  self.formated_time = ko.computed(function() {
    seconds = self.created_at().getSeconds();
    minutes = self.created_at().getMinutes();
    hours = self.created_at().getHours();
    return hours + ':' + minutes + ':' + seconds;
  });
}

function Criteria(path, operator, value) {
    var self = this;
    self.path = ko.observable(path);
    self.operator = ko.observable(operator);
    self.value = ko.observable(value);
}

function Action(type, params) {
    var self = this;
    self.type = ko.observable(type);
    self.parameters = ko.observableArray(params);
}

function Alarm() {
    var self = this;
    self.criteria = ko.observableArray([]);
    self.action = ko.observable(new Action('mail', ['']));
    self._id = ko.observable()

    self.add_criterion = function() {
        self.criteria.push(new Criteria("", "==", ""));
    }

    self.remove_criterion = function(criterion) {
        self.criteria.remove(criterion);
    }
}

