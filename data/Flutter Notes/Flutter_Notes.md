# Flutter Notes

## Widget Hierarchy

A Flutter app is a tree of nested widgets. The root is `MaterialApp`, which wraps a `Scaffold`.

`Scaffold` provides the basic visual layout including `AppBar` and `body`.

```dart
void main() {
  runApp(
    MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Widget Hierarchy')),
        body: Center(
          child: Column(
            children: [
              Text('Hello, Flutter!'),
              ElevatedButton(
                onPressed: () {},
                child: Text('Click Me'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
```

## Stateless Widget

A StatelessWidget is immutable. Its UI does not change after it is built.

It has no internal state. It renders static content that does not react to user interactions or data changes.

## Stateful Widget

A StatefulWidget is mutable. Its UI can change in response to user actions or data updates.

State is updated using the `setState()` method, which triggers a UI rebuild.

Example use case: a counter button that increments a number on each tap.

## build() Method

The `build()` method returns the widget tree for a given widget.

It is called every time the state updates, causing the widget tree to rebuild with the latest data.

---

## Controllers in Flutter

Controllers manage the state or behavior of specific widgets such as `TextField`, `ScrollView`, and animations.

They are similar to the `useState` hook in React. They track the current state of a widget.

Common controllers include `TextEditingController`, `ScrollController`, and `AnimationController`.

## TextEditingController Example

```dart
class _TextControllerExampleState extends State<TextControllerExample> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose(); // Free resources
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          TextField(controller: _controller),
          ElevatedButton(
            onPressed: () {
              print('Text: ${_controller.text}');
              _controller.clear();
            },
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }
}
```

Always call `dispose()` on controllers to free memory when the widget is removed.

---

## Keys in Flutter

Keys are used to preserve widget state and uniquely identify widgets during UI rebuilds.

When Flutter rebuilds the UI, it matches widgets by their position. If order changes (e.g., in a list), states can get mixed up. Keys fix this by letting Flutter identify the correct widget.

## ValueKey

Use `ValueKey` when you have a unique identifier such as an ID.

```dart
ListView.builder(
  itemBuilder: (context, index) {
    return ListTile(
      key: ValueKey(todoList[index].id),
      title: Text(todoList[index].title),
    );
  },
)
```

## UniqueKey

Use `UniqueKey` when you want Flutter to always treat a widget as completely new.

```dart
Container(key: UniqueKey())
```

## GlobalKey

`GlobalKey` allows access to a widget's state from anywhere in the app.

It is commonly used with forms to validate or save form fields from outside the widget tree.

## ObjectKey

`ObjectKey` is used when passing an entire object as an identifier.

```dart
ListTile(key: ObjectKey(user))
```

---

## Async and Await

`async` and `await` are used to handle asynchronous operations without blocking the UI.

Marking a function with `async` allows it to use `await`, which pauses execution until a Future completes.

## Future in Flutter

A `Future` represents a value that will be available at some point in the future.

It is used for async operations such as API calls, file reads, or database queries.

A Future can complete with a value (success) or an error (failure).

## FutureBuilder Widget

`FutureBuilder` is a widget that builds UI based on the state of a Future.

It handles three states: loading, success, and error.

```dart
FutureBuilder<String>(
  future: fetchData(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return CircularProgressIndicator();
    } else if (snapshot.hasError) {
      return Text('Error: ${snapshot.error}');
    } else {
      return Text('Data: ${snapshot.data}');
    }
  },
)
```

## Streams in Flutter

A Stream is like a pipe through which data or events flow continuously.

A `StreamController` pushes values into the stream. Listeners at the other end receive each emitted value or event. Multiple listeners can subscribe to the same stream.

Streams are asynchronous and used for real-time, ongoing data.

## StreamBuilder Widget

`StreamBuilder` is a widget that listens to a Stream and rebuilds the UI whenever the stream emits a new event.

Think of it as a real-time listener for data changes.

Use cases include: live chat messages (Firebase snapshot), live scores, push notifications, and sensor or device updates.

```dart
Stream<int> counterStream = Stream.periodic(
  Duration(seconds: 1),
  (count) => count + 1,
);
```

`counterStream` emits an integer every second. Use `StreamBuilder` to display it in the UI.

## StreamTransformer

`StreamTransformer` is used to filter or transform stream data before it reaches the listener.

It sits between the stream source and the listener, processing each event.

---

## Layout Widgets

Layout widgets arrange, position, and organize other widgets on the screen.

Examples include: `Row`, `Column`, `Stack`, `Container`, `Expanded`, and `Flexible`.

Single-child layout widgets (e.g., `Align`, `Center`) accept only one child. Multi-child layout widgets (e.g., `Column`, `Row`) accept multiple children.

## ListView Builder

`ListView.builder` is used when rendering a list from a known array of data.

It lazily builds items on demand, making it efficient for long lists.

```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    return ListTile(title: Text(items[index]));
  },
)
```

## Expanded Widget

`Expanded` makes a child widget take up all remaining available space in a `Row` or `Column`.

Use it when you want a widget to fill all leftover space.

## Flexible Widget

`Flexible` lets a child widget take only as much space as it needs, up to the available space.

Unlike `Expanded`, it does not force the widget to fill all remaining space.

## Responsiveness in Flutter

Flutter provides three main tools for building responsive UIs:

1. `MediaQuery` — reads screen dimensions and orientation.
2. `Flexible` — takes only the space it needs.
3. `Expanded` — takes all remaining space.

---

## Ternary Operator

The ternary operator is a one-line `if-else` using `?` and `:`.

```dart
String result = isLoggedIn ? 'Welcome' : 'Please log in';
```

Use it for simple conditional expressions to keep code concise.

## Mixins

Mixins allow reusable code to be shared across multiple classes without using inheritance.

Flutter does not support multiple inheritance, so mixins solve this limitation.

```dart
mixin Logger {
  void log(String message) {
    print('Log: $message');
  }
}

class User {
  String name;
  User(this.name);
}

class Admin extends User with Logger {
  Admin(String name) : super(name);
}

void main() {
  final admin = Admin('Alice');
  admin.log('Admin created'); // Log: Admin created
}
```

---

## Context in Flutter

`context` is a reference to the location of a widget in the widget tree.

It provides access to theme data, navigation, and inherited widgets from parent nodes.

## Snapshot in Flutter

A `snapshot` is a package of data provided by `FutureBuilder` or `StreamBuilder`.

It contains the connection state, data, and any error from an async operation.

---

## SDK in Android Development

An SDK (Software Development Kit) is a reusable library or toolkit that provides functionality other apps or developers can use without accessing the full source code.

In Flutter/Android, you can package logic or UI components into an SDK. Others integrate it like any third-party library (e.g., Firebase SDK, Facebook SDK).

## Bridging and Channels in Flutter

Platform Channels are used to call native Android or iOS code from Flutter.

This is called bridging. It allows Flutter to access native device APIs not available through Flutter plugins.

## Platform Detection in Flutter

Flutter provides a way to identify whether the current device is running Android or iOS.

This is used to render platform-specific UI or call platform-specific APIs conditionally.
