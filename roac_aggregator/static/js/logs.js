$(function() {
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

  function LogModel() {
    self.log = ko.observableArray([]);
    self.info = ko.observable();
    self.info_text = ko.computed(function() {
        return JSON.stringify(self.info(), undefined, 2);
    });

    self.populate_log = function() {
      //replaces the content of the log by updated info.
      $.getJSON("/api/v1/logs", function(data) {
        var mappedRecords = $.map(data, function(record) {
          created_at = new Date(Date.parse(record.created_at));
          return new Record(record.name, created_at, record.results);
        });
        self.log(mappedRecords)
      });
    };

    self.repeat_populate_log = function() {
      self.populate_log();
      setTimeout(function() {self.repeat_populate_log();}, 1000);
    }

    self.show_info = function(record) { 
      //requires a bootstrap modal called #modal that displays info_text
      self.info(record.results());
      $('#modal').modal();
    }

    self.repeat_populate_log();
  }

  ko.applyBindings(new LogModel());
});

