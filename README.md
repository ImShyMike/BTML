# BTML

HTML but with brackets :D

 ---

Ever felt like plain HTML is lacking some brackets? Worry no more, BTML fixes that for you!

Plain HTML (bad):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>My First Web Page</title>
</head>
<body>
  <h1>Welcome to My Web Page</h1>
  <p>This is a simple HTML example with a button below.</p>
  <button onclick="alert('Hello, world!')">Click Me</button>
</body>
</html>
```

BTML (much better):

```js
!html!
html[lang="en"] {
  head {
    meta[charset="UTF-8"].
    title "My First Web Page"
  }
  body {
    h1 "Welcome to My Web Page"
    p "This is a simple HTML example with a button below."
    button[onclick="alert('Hello, world!')"] "Click Me"
  }
}
```
