# App Template File

This is the template file for the `App` class of page that the site's generator, PageMaker, utilizes.

The `App` class is unique from the other types of pages on this site in that the page can host an interactive applet. This can include a wide variety of things like a full javascript app &mdash; of which [Coin Flip](mikeverwer.github.io/apps/coin_flip.html) is an example &mdash; or an embedding, like [Cyber Events Dashboard](mikeverwer.github.io/apps/cyber_events.html).

## Requirements

`App` pages have specific requirements that other page types do not. Apps require multiple files in a specific place with specific names. For the following, [app-name] is a substitute for the apps **actual** html filename. This name must be identical to the html filename for the app, PageMaker expects them to match.

An `App` can have up to four files that must have the following naming conventions:

`[app-name].css`
: Any CSS that the app requires should go in this file. This CSS file gets loaded last in the stylesheet cascade.

`[app-name].js`
: Any javascript that the app requires goes in here.

`content.html`
: The html content required for the app. Everything in this file gets injected directly into the `#app-container` div, which is the first child of the `.main-section` div, therefore there should be no `<head>` or `<body>` tags in the file.

`deps.txt`
: Any external scripts that are required for the app should be listed here. Only the resource URL should be included, with each URL on a separate line.
: For example, 
    ```
    https://cdn.plot.ly/plotly-3.5.0.min.js
    https://cdn.jsdelivr.net/npm/jquery@3.6.4/dist/jquery.min.js 
    ```

None of the files are strictly required by PageMaker, include them only if the app itself requires them; `content.html` is a soft exception since the app would not appear on the page without any HTML placing it there.

All of the included files must be placed in a folder with the same name as the app: i.e. [app-name] and this folder must be placed in `\assets\apps` from root as shown here.

```
assets/
└─ apps/
   └─ [app-name]/
      ├─ [app-name].css
      ├─ [app-name].js
      ├─ content.html
      └─ deps.txt
```

The `.md` article file should be placed in `\assets\docs\apps\`