# BTML

[![PyPI - Version](https://img.shields.io/pypi/v/btml.svg)](https://pypi.org/project/btml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/btml.svg)](https://pypi.org/project/btml)

HTML but with curly brackets

 ---

Ever felt like plain HTML is lacking some curly brackets? Worry no more, BTML fixes that for you!

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

## Installation

BTML can be installed from PyPI using pip:

```bash
pip install btml
```

## Usage

After installing, run:

```bash
btml
```

or, if that doesn't work:

```bash
pythom -m btml
```

## License

`btml` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
