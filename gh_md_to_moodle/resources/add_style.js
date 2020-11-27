var stylesheet =
  "https://github.githubassets.com/assets/gist-embed-52b3348036dbd45f4ab76e44de42ebc4.css";
var head = document.getElementsByTagName("head")[0];
var link = document.createElement("link");
link.rel = "stylesheet";
link.href = stylesheet;
head.appendChild(link);
// add custom css to make syntax-hl bigger font-size
var css = `
    .highlight {
        font-size: 1rem !important;
    }
    .box-body {
        padding: 1rem !important;
    }
    .code-container {
        width: 100%;
        padding-right: 15px;
        padding-left: 15px;
        margin-right: auto;
        margin-left: auto;
        max-width: 1140px;
    }
    code {
        color: #e83e8c;
        word-wrap: break-word;
    }`;
var style = document.createElement("style");
head.appendChild(style);
style.appendChild(document.createTextNode(css));
