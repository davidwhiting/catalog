# UMGC Catalog Project using H2O Wave

## Overview
The purpose behind this project is to create a self-serve registration app that follows the UMGC course catalog. We chose H2O Wave (http://wave.h2o.ai) as the UI since 

1. it is written in Python so HTML, Javascript, etc. skills are not necessarily needed, 
2. it is more stable in production environments than competing choices such as Streamlit (e.g., AT&T has hundreds of H2O Wave apps in production within their corporate environment),
3. authorship in Python enables the use of many Python machine learning and AI libraries that are not directly available in D3, for instance.

## Files

The files required by the Wave app include:

- `app.py`
- `cards.py`
- `templates.py`
- `utils.py`
- `class_d3.js`
- `UMGC.db`


## Appendix

### Notes on Events (summary from chatgpt, ymmv):

The `on_event` method and the `@on()` decorator are both used for event handling in H2O Wave, but they have slightly different use cases and syntax.

#### `on_event` method:

Syntax: `card.on_event(handle_event_function)`

This method is typically used when you want to attach an event handling function directly to a specific UI component, such as a card, button, or input field. It allows you to define custom event handling logic for a specific UI component within your Wave app. You can attach multiple event handling functions to the same component, and each function can handle different types of events.

#### `@on()` decorator:

Syntax: `@on('event_type')`

This decorator is used to define event handling functions outside of the UI component's definition, typically in a separate module or class. It is useful when you want to organize your event handling functions separately from the UI component definitions, keeping your code clean and modular. You specify the event type as an argument to the decorator (`@on('event_type')``), indicating which type of event the function should handle. You can attach a single event handling function to multiple UI components by specifying the same event type in multiple `@on()` decorators.

In summary, both methods serve the same purpose of handling events in H2O Wave apps, but the choice between them depends on your preference and the structure of your application. Use the `on_event` method when you want to attach event handling functions directly to UI components, and use the `@on()` decorator when you want to define event handling functions separately and attach them to multiple components.

### Await with events

In Python, `async` functions typically require the `await` keyword when calling other asynchronous functions inside them. However, when you're defining an event handler in H2O Wave, you don't actually need to `await` the `on_event` method call.

The reason for this is that the `on_event` method doesn't return a coroutine object that needs to be awaited. Instead, it simply registers the event handling function with the card. When an event occurs, the Wave framework will automatically call the event handling function asynchronously without requiring an `await` statement.

So, in the case of registering an event handler with `card.on_event(handle_event)`, you don't need to `await` it. The `await` keyword is not necessary here because the `on_event` method doesn't return an awaitable object.

### Notes on UMGC Online Menus

- The Healthcare Administration MS degree shows up online but not in the catalog
- Accounting graduate certificate shows up online but not in catalog
