$(function() {
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
            console.log("asdf");
        }

        self.remove_criterion = function(criterion) {
            self.criteria.remove(criterion);
        }
    }

    function AlarmsModel() {
        var self = this;
        self.alarms = ko.observableArray([]);

        self.action_possib = ko.observableArray(['mail']);
        self.oper_possib = ko.observableArray(['gt', 'gte', 'lt', 'lte', '=='])

        self.update_alarms = function() {
            $.getJSON('/api/v1/alarms/', function(data) {
                alarms = $.map(data, function(alarm) {
                    a = new Alarm();
                    a.criteria($.map(alarm.criteria, function(criteria) {
                        return new Criteria(criteria.path,
                                            criteria.operator, criteria.value);
                    }));
                    a.action(new Action(alarm.action.type, alarm.action.parameters));
                    a._id(alarm._id);
                    return a;
                });
                self.alarms(alarms)
            });
        }

        self.save_alarms = function() {
            console.log(ko.toJSON(self.alarms));
        }

        self.add_alarm = function() {
            a = new Alarm()
            self.alarms.push(a);
        }

        self.remove_alarm = function(alarm) {
            self.alarms.destroy(alarm);// Doesn't actually delete, but marks for deletion
        }

        self.update_alarms();
    }

    ko.applyBindings(new AlarmsModel());
});

