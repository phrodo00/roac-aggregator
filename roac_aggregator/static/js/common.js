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

