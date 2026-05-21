# React Native & JavaScript Interview Knowledge Base

## Overview

This knowledge base covers React Native and JavaScript concepts prepared for technical interviews. It includes core fundamentals, hooks, state management, navigation, performance optimization, asynchronous JavaScript, advanced concepts, scenario-based debugging, and data structure algorithm questions. Every section is explained in depth with code examples and real-world context.

---

## React vs React Native

React is a JavaScript library used to build web applications that run inside a browser. It works with HTML, CSS, and the Document Object Model (DOM) to render UI. React Native, on the other hand, is a framework used to build mobile applications for Android and iOS. Instead of HTML elements, React Native uses native mobile UI components such as View, Text, Image, and ScrollView. React Native does not use the DOM at all. Styling in React Native is done using the StyleSheet API rather than traditional CSS files.

The Document Object Model (DOM) is a tree structure that the browser creates when an HTML page loads. For example, the HTML `<h1>Hello</h1>` is represented in the DOM as Document → h1 → "Hello". React (web) works with a Virtual DOM to optimize updates, while React Native bypasses this entirely and communicates directly with native mobile components.

---

## React Native Architecture

React Native's architecture consists of three main threads that work together to render and run the application.

The JavaScript Thread is responsible for compiling and running all JavaScript code. When code is executed, it runs in this thread.

The Shadow Thread (also called the Layout Thread) handles all layout calculations — such as computing sizes and CSS-like properties — before and during UI rendering. All calculations that happen before and during UI rendering occur in the Shadow Thread.

The UI Thread (also called the Native Thread) is responsible for actually rendering the components on screen.

The traditional architecture used a Bridge to communicate between the JavaScript Thread and the Native Thread. The newer architecture replaces the Bridge with JSI (JavaScript Interface) and Fabric, which allows direct communication between JavaScript and native modules for better performance.

---

## Core React Native Components

React Native provides a set of built-in components called Core Components that serve as the building blocks of the UI. These include View (a container similar to a div in web), Text (for displaying text), Image (for displaying images), ScrollView (for scrollable containers), TextInput (for user input), Button and Pressable and TouchableOpacity (for tappable elements), FlatList (for rendering large optimized lists), SectionList (for sectioned lists), SafeAreaView (for safe display areas on notch devices), KeyboardAvoidingView (to adjust layout when the keyboard appears), and ActivityIndicator (a loading spinner).

The difference between View and Text is important to understand. View is a container component and does not render text directly. Text supports inline text styling and is the only component used to display text content.

---

## React Native Styling and Layout

React Native does not use CSS files. Instead, styling is done using inline style objects or the StyleSheet.create API. The layout system used in React Native is Flexbox, powered by the Yoga Layout Engine. Flexbox in React Native works similarly to CSS Flexbox on the web, but with a few key differences in default values.

The main Flexbox properties used in React Native are flex (which defines how much of available space a component takes), flexDirection (which controls the primary axis: row or column), justifyContent (which aligns items along the primary axis), and alignItems (which aligns items along the cross axis).

An important distinction between flex and flexGrow is that flex: 1 distributes available space proportionally among siblings, while flexGrow expands the component to take the entire available space of its parent view.

Responsiveness in React Native is achieved through three approaches. First, Flexbox Layout using flex, justifyContent, and alignItems. Second, Percentage-based dimensions such as width: "50%". Third, the Dimensions API using Dimensions.get("window") to get the screen width and height dynamically.

---

## React Native Components — Class vs Functional

Functional components are JavaScript functions that return UI. They use React Hooks like useState and useEffect to manage state and lifecycle events. Class components are ES6 classes that extend React.Component and manage state using this.state and lifecycle methods such as componentDidMount. Modern React Native development predominantly uses functional components with Hooks.

Pure Components avoid unnecessary re-renders when the incoming state or props are the same as before. In class components, you extend PureComponent instead of Component. In functional components, you wrap the component with React.memo() to achieve the same behavior.

Higher-Order Components (HOCs) are functions that take a component as an argument and return a new component with additional behaviors or props injected. They are useful for code reuse across multiple components without modifying the original component.

Custom Components are reusable components built by the developer to encapsulate business logic and UI. Custom Hooks are reusable functions where business logic is extracted from components, allowing the logic to be shared without duplicating code.

---

## React Hooks

Hooks are special functions in React that allow functional components to use state and lifecycle features without writing class components.

## useState

useState is used to store and update data (state) inside a component. It returns the current state value and a setter function. An important behavioral characteristic is that useState updates are asynchronous — meaning state does not update immediately after calling the setter. To safely update state based on its previous value, use the functional form: `setCount(prev => prev + 1)`.

## useEffect

useEffect handles side effects such as API calls, timers, subscriptions, and lifecycle events in functional components. It takes a callback function, an optional dependency array, and an optional cleanup function.

When no dependency array is provided, useEffect runs after every render. When an empty dependency array is provided, it runs only once after the initial mount, behaving like componentDidMount. When specific values are placed in the dependency array, it runs every time those values change, behaving like componentDidUpdate. The cleanup function returned from useEffect runs before the component unmounts or before the effect runs again, and it behaves like componentWillUnmount.

```javascript
useEffect(() => {
  console.log("Mounted");
  return () => {
    console.log("Unmounted");
  };
}, []);
```

## useRef

useRef stores a mutable value that persists across renders without causing a re-render when updated. It is commonly used to access DOM elements directly (such as focusing a TextInput), to store the previous value of state, and to prevent unnecessary re-renders for performance optimization.

## useCallback and useMemo

useCallback returns a memoized (cached) version of a callback function. It only recreates the function when its dependencies change. useMemo returns a memoized value — the result of an expensive computation — and only recomputes it when dependencies change. Both hooks are used for performance optimization to prevent unnecessary re-renders.

## useReducer

useReducer is used for managing local component state with complex logic through dispatched actions. It is the local-component counterpart to Redux. Redux is used for global state management across the entire application through a centralized store containing multiple reducers.

## useContext

useContext (Context API) provides a solution to the prop drilling problem. It allows a value (state or functions) to be provided at a high level in the component tree and consumed at any depth without manually passing props through every intermediate component. It uses a Provider to supply values and the useContext hook (or a Consumer) to access them.

## useLayoutEffect

The primary difference between useLayoutEffect and useEffect is timing. useEffect runs after the render is painted to the screen and is suitable for API calls, timers, and subscriptions. useLayoutEffect runs before the render is painted to the screen and is suitable for animations and DOM measurements that need to happen synchronously before the user sees the update.

---

## Props vs State

State is defined within a component and is mutable — it can be changed by the component itself using the setter function provided by useState or by dispatch in useReducer. Props are immutable values passed from a parent component to a child component. The child component cannot modify its own props.

Data flows in React Native in two directions. Parent-to-child data flows via props. Child-to-parent data flows via callback functions passed as props.

```javascript
const Parent = () => {
  const handlePress = () => {
    console.log("Button clicked in child");
  };
  return <Child onPress={handlePress} />;
};

const Child = (props) => {
  return <Button title="Click Me" onPress={props.onPress} />;
};
```

Prop drilling refers to the problem where props must be passed through many intermediate components that do not need them, just to reach a deeply nested child. The Context API solves this.

---

## State Management with Redux Toolkit

Redux Toolkit is a global state management library. It has two core concepts: the Store and Slices. The Store is the central place where all global state is stored. A Slice combines Reducers (functions that specify how state changes in response to actions) and Actions (descriptors of what happened) into a single unit. Redux is preferred when state needs to be shared across many components throughout the entire application.

---

## Navigation in React Native

React Native does not have a built-in navigation system. Navigation is handled using third-party libraries, most commonly React Navigation. There are three primary navigators.

Stack Navigator manages a stack of screens and provides screen transition animations. It maintains a navigation history so users can go back to previous screens. Tab Navigator creates parallel navigation using bottom or top tabs where each tab represents an independent screen or stack. Drawer Navigator provides a slide-in menu drawer for navigation.

---

## Lists and Performance

FlatList is the recommended component for rendering large lists in React Native. It uses lazy loading, meaning it only renders the items that are currently visible on screen, which greatly improves performance. ScrollView, in contrast, renders all of its child components at once regardless of visibility, making it unsuitable for large datasets.

The keyExtractor prop in FlatList is a function that returns a unique string key for each item. It helps React identify items uniquely so that it can efficiently determine which items have changed, been added, or been removed without re-rendering the entire list.

```javascript
<FlatList
  data={data}
  keyExtractor={(item) => item.id.toString()}
  renderItem={({ item }) => <Text>{item.name}</Text>}
/>
```

Performance issues in React Native are commonly caused by heavy re-renders, large unoptimized lists, unnecessary state updates, and heavy computations on the JavaScript thread. Solutions include using FlatList instead of ScrollView, using React.memo, useMemo, and useCallback to prevent unnecessary re-renders, and implementing pagination using hooks such as useInfiniteQuery.

---

## API Calls in React Native

API calls in React Native are made using either the built-in fetch API or the third-party Axios library. Both return Promises and are used inside useEffect or async functions.

Multiple API calls can be made simultaneously using Promise.all (which fails fast if any one promise fails), Promise.allSettled (which waits for all promises and returns their individual results regardless of success or failure), or axios.all.

To cancel an API request, the AbortController API is used. This is particularly useful in search bars (to cancel the previous request when the user types a new character), in auto-refresh scenarios, and to prevent duplicate requests.

```javascript
const controller = new AbortController();
fetch(url, { signal: controller.signal });
controller.abort(); // Cancel the request
```

---

## Handling Forms

Forms in React Native are handled in two ways. Controlled components use React state to control the value of inputs. Uncontrolled components manage their own internal state and their values are accessed using refs. Third-party libraries like react-hook-form use a Controller component to integrate with React Native inputs for more complex form scenarios.

---

## Local Storage Options

AsyncStorage is the basic key-value persistent storage system for React Native, suitable for storing small amounts of data such as user preferences or tokens. MMKV is a high-performance alternative to AsyncStorage, based on the same library used by WeChat, offering significantly faster read and write operations. SQLite is used for storing structured relational data locally, suitable for complex data with relationships and queries.

---

## Device Features and Native Modules

Device features such as camera access, geolocation, push notifications, and sensors are accessed through native libraries. For example, react-native-camera for camera access and react-native-geolocation-service for location access.

The Platform module in React Native tells the developer whether the current device is Android or iOS using Platform.OS. Platform-specific code can also be placed in files with the .ios.js or .android.js extension, and React Native will automatically pick the correct file. Native Modules provide a bridge between JavaScript and native Android/iOS code for features not covered by existing libraries.

---

## Debugging in React Native

React Native apps are debugged using console.log for basic logging, Flipper (a desktop app for inspecting network requests, logs, and component trees), and React DevTools for inspecting the component tree and state.

Common debugging scenarios include API calling twice in development (caused by React Strict Mode intentionally running effects twice), undefined state (caused by accessing state before it has been set), and navigation not working (usually caused by missing NavigationContainer wrapping the app).

---

## GraphQL

GraphQL uses a single endpoint instead of multiple REST endpoints. Within that single endpoint, there are two types of operations: Queries (for reading data, equivalent to GET) and Mutations (for writing data, equivalent to POST, PUT, and DELETE). This means one URL handles many actions, unlike REST which maps different URLs to different resources.

---

## Authentication Patterns

OAuth is used for secure authentication without requiring the user to share a password directly — for example, "Login with Google". The OAuth flow delegates authentication to a trusted third-party identity provider. JWT (JSON Web Token) is a token format used to identify who the user is. The token is generated upon login and passed with every subsequent API request so the server can verify the user's identity without re-authenticating each time.

---

## var, let, and const

var is function-scoped and can be both re-declared and re-assigned. Importantly, var is hoisted to the top of its scope. let is block-scoped and can be re-assigned but cannot be re-declared within the same scope. const is block-scoped and cannot be re-assigned after declaration, but importantly, the properties of a const object can still be mutated.

## Hoisting

Hoisting is JavaScript's behavior where variable and function declarations are moved to the top of their scope during the compilation phase, before execution begins. This means you can call a function declared with the function keyword before its definition in the code. var variables are hoisted but initialized as undefined. let and const are hoisted but are in a "temporal dead zone" until their declaration is reached.

## Closures

A closure is a function that remembers and has access to variables from its outer (enclosing) function scope even after the outer function has finished executing. Closures are the mechanism behind the "count remembering" behavior seen in counter functions.

```javascript
function outer() {
  let count = 0;
  function inner() {
    count++;
    console.log(count);
  }
  return inner;
}

const counter = outer();
counter(); // 1
counter(); // 2
counter(); // 3
```

## Closures Bank Account Example

A real-world use case for closures is implementing a bank account where the balance is private and can only be modified through exposed methods.

```javascript
function createBankAccount(balance) {
  return {
    deposit(amount) {
      balance += amount;
      console.log(balance);
    },
    getBalance() {
      return balance;
    }
  };
}

const account = createBankAccount(100);
account.deposit(50); // 150
console.log(account.getBalance()); // 150
```

## Closures Counter with Increment and Decrement

```javascript
function counter() {
  let count = 0;
  return {
    increment() { count++; return count; },
    decrement() { count--; return count; }
  };
}

const c = counter();
console.log(c.increment()); // 1
console.log(c.increment()); // 2
```

## Scope Chain

When JavaScript looks up a variable, it searches in the current scope first, then in the parent scope, and continues upward to the global scope. This chain of nested lexical environments is called the scope chain.

## == vs ===

The double equals operator (==) uses loose comparison with type coercion, meaning it converts values to the same type before comparing. The triple equals operator (===) uses strict comparison without any type coercion. For example, `"5" == 5` returns true because the string is coerced to a number, but `"5" === 5` returns false because the types are different.

---

## Arrow Functions vs Regular Functions

Arrow functions use the `=>` syntax and do not require the function keyword. They have several important differences from regular functions.

Arrow functions do not have their own `this` — they inherit `this` from their surrounding lexical scope. Regular functions have their own `this` context that depends on how they are called.

Arrow functions do not have a built-in arguments object (use rest parameters instead). Arrow functions cannot be used as constructors with the new keyword. Arrow functions are not hoisted, so they must be defined before being called.

## Arrow Functions Implicit Return

Arrow functions support implicit returns: in a single-line arrow function without curly braces, the result of the expression is automatically returned without needing the return keyword. Example: `const add = (a, b) => a + b`.

To implicitly return an object literal from an arrow function, the object must be wrapped in parentheses: `const getUser = () => ({ name: 'John' })`. Without parentheses, the curly braces are interpreted as a function block.

## Arrow Functions and this Binding

The call(), apply(), and bind() methods cannot override the `this` value of an arrow function because arrow functions inherit `this` from their scope and do not have their own.

Arrow functions are commonly used in setTimeout or event listeners precisely because they preserve the `this` context of the surrounding class or function, avoiding the need for `.bind(this)`.

---

## The `this` Keyword

The value of `this` in JavaScript depends entirely on how a function is called, not where it is written.

In global scope, `this` refers to the window object (or undefined in strict mode). Inside an object method defined with a regular function, `this` refers to the object itself.

Inside an arrow function used as an object method, `this` does not refer to the object — it inherits from the outer scope (usually window), so `this.name` would be undefined.

Inside a constructor function called with new, `this` refers to the newly created object. Inside a class method, `this` refers to the class instance.

Inside a setTimeout callback using a regular function, `this` refers to the global object. Using an arrow function inside setTimeout fixes this by inheriting `this` from the outer method.

```javascript
// this in object method
const user = { name: "Moeez", greet() { console.log(this.name); } };
user.greet(); // "Moeez"

// this in arrow function (problem)
const user2 = { name: "Moeez", greet: () => { console.log(this.name); } };
user2.greet(); // undefined

// fix setTimeout this issue
const user3 = {
  name: "Moeez",
  greet() {
    setTimeout(() => { console.log(this.name); }, 1000);
  }
};
user3.greet(); // "Moeez"
```

## call(), apply(), and bind()

call() executes a function immediately and lets you pass the `this` context along with arguments one by one:

```javascript
function greet(city) { console.log(this.name + " from " + city); }
const user = { name: "Moeez" };
greet.call(user, "Lahore"); // "Moeez from Lahore"
```

apply() is identical to call() except arguments are passed as an array:

```javascript
greet.apply(user, ["Lahore", "Pakistan"]); // "Moeez from Lahore, Pakistan"
```

bind() does not execute the function immediately. It returns a new function with `this` permanently bound to the provided context:

```javascript
const newFunc = greet.bind(user);
newFunc(); // "Moeez"
```

---

## Call by Value vs Call by Reference

Call by Value means the function receives a copy of the value, so changes inside the function do not affect the original variable. Primitive types (numbers, strings, booleans) are passed by value.

```javascript
let a = 10;
function changeValue(x) { x = 20; }
changeValue(a);
console.log(a); // still 10
```

Call by Reference means the function receives a reference to the original object, so changes inside the function do affect the original. Objects and arrays are passed by reference.

```javascript
let obj = { name: "Doe" };
function changeValue(obj) { obj.name = "John"; }
changeValue(obj);
console.log(obj.name); // "John"
```

---

## Deep Copy vs Shallow Copy

A shallow copy copies only the top-level properties of an object. Nested objects still reference the original, so modifying a nested object in the copy also changes the original.

```javascript
const shallowCopy = Object.assign({}, original);
```

A deep copy copies all levels of the object, so changes in the copy do not affect the original at any depth.

```javascript
const deepCopy = JSON.parse(JSON.stringify(original));
```

---

## Asynchronous JavaScript

## The Event Loop

JavaScript is single-threaded, which means it can only do one thing at a time. The event loop is the mechanism that allows JavaScript to handle asynchronous operations without blocking the main thread. It coordinates between four components: the Call Stack (where synchronous code runs), Web APIs (where async operations like setTimeout and fetch are handed off), the Callback Queue (also called the macrotask queue, where callbacks from setTimeout and similar APIs wait), and the Microtask Queue (where Promise callbacks wait, and which is processed before the callback queue).

The critical insight is that Promises (microtasks) are always processed before setTimeout callbacks (macrotasks):

```javascript
console.log("Start");
setTimeout(() => console.log("Timeout"), 0);
Promise.resolve().then(() => console.log("Promise"));
console.log("End");

// Output:
// Start
// End
// Promise
// Timeout
```

## Promises

A Promise is an object that represents the eventual completion or failure of an asynchronous operation. Promises are used for API calls, file reading, and any operation that takes time to complete. They have three states: pending, fulfilled (resolved), and rejected.

```javascript
const promise = new Promise((resolve, reject) => {
  resolve("Done");
});

fetchData()
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.log(err));
```

## Async/Await

async/await is syntactic sugar over Promises. Every async function always returns a Promise. The await keyword pauses the execution of the async function until the Promise resolves, making asynchronous code look and behave like synchronous code.

```javascript
async function getData() {
  try {
    const res = await fetch(url);
    const data = await res.json();
    console.log(data);
  } catch (err) {
    console.log(err);
  }
}
```

## Sequential vs Parallel Execution

Running awaited calls one after another is sequential and slower because each waits for the previous to finish. Running them with Promise.all is parallel and faster because all start simultaneously.

```javascript
// Sequential (slower)
await task1();
await task2();

// Parallel (faster)
await Promise.all([task1(), task2()]);
```

## Promise.all vs Promise.allSettled

Promise.all runs all promises in parallel and resolves when all succeed. If any one promise fails, it immediately rejects and the results of the others are discarded. Promise.allSettled also runs all in parallel but always resolves with an array of result objects for every promise, regardless of whether they succeeded or failed — making it safe when you need all results even if some fail.

## Callback Hell

Callback Hell is a situation where multiple nested callbacks are used inside each other, making the code very hard to read, maintain, and debug. It occurs when handling multiple asynchronous operations that depend on each other.

```javascript
getUser(function(user) {
  getOrders(user, function(orders) {
    getDetails(orders, function(details) {
      console.log(details);
    });
  });
});
```

This is solved by using Promises with .then chaining or async/await.

---

## Advanced JavaScript Concepts

## Currying

Currying is a functional programming technique that transforms a function with multiple arguments into a series of functions that each take a single argument. It is used to create reusable and specialized functions by fixing some parameters early. Currying is commonly used in logging utilities, event handling, and libraries like Lodash and Ramda.

```javascript
const add = a => b => c => a + b + c;
console.log(add(1)(2)(3)); // 6

function logger(level) {
  return function(message) {
    console.log(`[${level}] ${message}`);
  };
}

const errorLog = logger("ERROR");
const infoLog = logger("INFO");
errorLog("Something failed");
infoLog("User logged in");
```

## Debouncing

Debouncing delays the execution of a function until after a specified period of inactivity. This means the function is only called after the user has stopped triggering events for the given delay duration. It is commonly used to optimize search input fields so the API is not called on every single keystroke.

```javascript
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}
```

## Throttling

Throttling limits a function to execute at most once per specified time interval. Regardless of how many times the event is triggered, the function will only run once every set period. It is used for scroll event handlers and window resize handlers.

```javascript
function throttle(fn, limit) {
  let flag = true;
  return function (...args) {
    if (!flag) return;
    fn.apply(this, args);
    flag = false;
    setTimeout(() => (flag = true), limit);
  };
}
```

The key difference between debounce and throttle is that debounce waits until the user stops (fires after silence), while throttle runs at a regular interval regardless (fires on a schedule).

## Prototypal Inheritance

Prototypal inheritance in JavaScript allows objects to inherit properties and methods from other objects through the prototype chain. Every object in JavaScript has an internal link to another object called its prototype. When you access a property on an object, JavaScript first looks at the object itself, then walks up the prototype chain until it finds the property or reaches null.

```javascript
const parent = {
  greet() { return "Hello"; }
};

const child = Object.create(parent);
console.log(child.greet()); // "Hello"
```

## Memoization

Memoization is an optimization technique where the results of expensive function calls are cached. When the same inputs are provided again, the cached result is returned instead of recomputing. The phrase "remember results so you don't repeat work" captures the concept well.

```javascript
function memoize(fn) {
  const cache = {};
  return function (n) {
    if (cache[n]) return cache[n];
    const result = fn(n);
    cache[n] = result;
    return result;
  };
}
```

## Event Delegation

Event delegation is a pattern where a single event listener is placed on a parent element instead of individual listeners on each child. When an event bubbles up from a child, the parent's listener handles it. This is more memory-efficient and works for dynamically added children.

## Destructuring and Spread Operator

Destructuring allows you to extract values from arrays or objects into individual variables in a concise syntax. The spread operator (...) expands the elements of an array or object inline, commonly used to copy arrays and objects or to merge them.

---

## JavaScript Data Types

Primitive data types in JavaScript are: string, number, boolean, null, undefined, bigint, and symbol. Non-primitive (reference) types are: object, array, and function. Arrays and objects are stored by reference in memory.

## Array Methods

map transforms every element in an array and returns a new array of the same length. filter returns a new array containing only the elements that pass a condition. forEach iterates over an array without returning anything. reduce reduces an array to a single value by accumulating results using a callback that receives the accumulator and current value. shift removes and returns the first element of an array. unshift adds one or more elements to the beginning of an array and returns the new length.

---

## Modules

Modules are blocks of code that can export functions, objects, or values from one file and import them in another. This enables code reuse and separation of concerns across files and components.

---

## TypeScript vs JavaScript

JavaScript is dynamically typed, meaning variables do not have declared types and can hold any value. TypeScript adds a static type system on top of JavaScript, requiring you to declare the type of each variable. In JavaScript, `let name = "Ali"; name = 123` produces no error. In TypeScript, `let name: string = "Ali"; name = 123` produces a compile-time error because 123 is not a string. TypeScript catches type errors before code runs, improving code quality and developer experience.

---

## Scenario-Based Debugging Questions

## API Calling Twice

When a useEffect with an API call runs twice in development, it is caused by React Strict Mode intentionally mounting, unmounting, and remounting components to help detect side effects. The fix is to either ignore this behavior in development (it does not happen in production) or add proper cleanup and guards inside the effect.

## this is Undefined

When `this` is undefined inside a function, it usually means the function is being called as a standalone function rather than as a method on an object. Extracting a method from an object and calling it separately loses the `this` binding.

```javascript
const obj = { name: "Umair", getName: function() { return this.name; } };
const fn = obj.getName;
console.log(fn()); // undefined

// Fix:
const fn = obj.getName.bind(obj);
```

## setTimeout(fn, 0) Does Not Run Immediately

Even with a delay of 0 milliseconds, setTimeout schedules the callback in the callback queue, which only runs after the call stack is empty and all microtasks (Promises) have resolved. This is why synchronous code always runs before a 0ms setTimeout.

## State Not Updating Immediately

State updates in React are asynchronous. Reading state immediately after calling the setter function returns the old value. The fix is to use the functional update form which guarantees access to the latest state:

```javascript
setCount(count + 1);
console.log(count); // still old value

// Fix:
setCount(prev => prev + 1);
```

## Infinite Re-Render Loop

A useEffect that updates a state variable listed in its own dependency array creates an infinite loop because every state update triggers a re-render, which triggers the effect again.

```javascript
// Problem:
useEffect(() => { setCount(count + 1); }, [count]);

// Fix: Remove dependency or adjust logic
```

## Closure Issue in Loops with var

When var is used in a for loop with setTimeout, all callbacks share the same variable because var is function-scoped. By the time the callbacks execute, the loop has finished and the variable holds its final value. Replacing var with let creates a new block-scoped binding for each iteration.

```javascript
// Problem:
for (var i = 0; i < 3; i++) { setTimeout(() => console.log(i), 1000); }
// Output: 3 3 3

// Fix:
for (let i = 0; i < 3; i++) { setTimeout(() => console.log(i), 1000); }
// Output: 0 1 2
```

## Object Keys Converted to Strings

In JavaScript, object keys are always strings. When an object is used as a key, it is converted to the string "[object Object]". If two different objects are used as keys on the same object, they both become "[object Object]" and the second assignment overwrites the first.

```javascript
const obj = {};
const a = { key: "a" };
const b = { key: "b" };
obj[a] = 123;
obj[b] = 456;
console.log(obj[a]); // 456 (b overwrote a)
```

## App Slow Rendering a List

Using ScrollView for large datasets renders all items at once, causing performance issues. The fix is to use FlatList, which only renders visible items (lazy loading), combined with memoization and pagination.

## UI Not Updating After State Change

Directly mutating state (such as `state.value = 10`) does not trigger a re-render because React does not detect the change. The fix is to always use the state setter function: `setState({ value: 10 })`.

---

## Data Structures and Algorithms in JavaScript

## Reverse a String

```javascript
function reverse(str) { return str.split('').reverse().join(''); }
```

## Check Palindrome

```javascript
function isPalindrome(str) { return str === str.split('').reverse().join(''); }
```

## Find Largest Number in Array

```javascript
function max(arr) { return Math.max(...arr); }
```

## Remove Duplicates from Array

```javascript
function unique(arr) { return [...new Set(arr)]; }
```

## Fibonacci Sequence

The recursive implementation: if n is 0 or 1, return n; otherwise return fib(n-1) + fib(n-2). The interviewer follow-up is to optimize this using memoization to avoid recalculating the same values.

```javascript
function fib(n) {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}
```

## Two Sum Problem

Given an array and a target sum, find the indices of two numbers that add up to the target. The optimal approach uses a hash map to store each number's index as you iterate, checking if the complement (target minus current number) already exists in the map.

```javascript
function twoSum(arr, target) {
  const map = {};
  for (let i = 0; i < arr.length; i++) {
    let diff = target - arr[i];
    if (map[diff] !== undefined) return [map[diff], i];
    map[arr[i]] = i;
  }
}
```

## Flatten a Nested Array

```javascript
function flatten(arr) { return arr.flat(Infinity); }
```

## Count Frequency of Array Elements

```javascript
function freq(arr) {
  return arr.reduce((acc, val) => {
    acc[val] = (acc[val] || 0) + 1;
    return acc;
  }, {});
}
```

---

## Key Interview Insights

Technical interviewers do not primarily test the ability to memorize definitions. They evaluate whether you can explain why something is used, trace code execution step-by-step, understand async behavior deeply, debug basic issues, optimize brute-force solutions, and build a small working feature.

The most important topics that separate strong candidates from average ones are closures, the `this` keyword and its context rules, the event loop and async execution order, the difference between FlatList and ScrollView, and basic debugging in React Native. Candidates who can confidently explain and demonstrate these concepts are already ahead of the majority of applicants.
