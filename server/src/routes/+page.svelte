<script lang="ts">
    import CodeMirror from "svelte-codemirror-editor";
    import { oneDark } from "@codemirror/theme-one-dark";
    import { LanguageSupport } from "@codemirror/language";
    import { StreamLanguage } from "@codemirror/language";

    import Footer from "../lib/components/Footer.svelte";
    import TopBar from "../lib/components/TopBar.svelte";

    let value = `!html!
html[lang="en"] {
  head {
    meta[charset="UTF-8"].
    title "My First Web Page"
  }
  body {
    <# This is a comment #>
    h1 "Welcome to My Web Page"
    p "This is a simple BTML example with a button below."
    button[onclick="alert('Hello, world!')"] "Click Me"
  }
}`;

    const btmlLanguage = StreamLanguage.define({
        name: "btml",
        token(stream, state) {
            // DOCTYPE declarations
            if (stream.match(/^!/)) {
                stream.skipTo("!");
                stream.match(/!/);
                return "string-2";
            }
            
            // BTML comments <# ... #>
            if (stream.match(/^<#/)) {
                stream.skipTo("#>");
                stream.match(/#>/);
                return "comment";
            }
            
            // Atoms (true, false, null)
            if (stream.match(/^(true|false|null)\b/)) {
                return "atom";
            }

            // Numbers (integers and floats)
            if (stream.match(/^\d+(\.\d+)?/)) {
                return "number";
            }

            // Any HTML tag name
            if (stream.match(/^[a-zA-Z][a-zA-Z0-9-]*(?=[\s\[\{]|$)/)) {
                return "tag";
            }
            
            // Attribute names and values inside brackets
            if (stream.match(/^\[/)) {
                return "bracket";
            }
            // Handle closing bracket
            if (stream.match(/^\]/)) {
                return "bracket";
            }
            if (stream.match(/^[a-zA-Z-]+(?==)/)) {
                return "attribute";
            }
            
            // Strings in quotes
            if (stream.match(/^"([^"\\]|\\.)*"/)) {
                return "string";
            }
            if (stream.match(/^'([^'\\]|\\.)*'/)) {
                return "string";
            }
            
            // Braces
            if (stream.match(/^[{}]/)) {
                return "bracket";
            }
            
            // Dots for self-closing tags
            if (stream.match(/^\./)) {
                return "operator";
            }
            
            stream.next();
            return null;
        }
    });

    const btmlSupport = new LanguageSupport(btmlLanguage);
</script>

<div class="flex flex-col w-screen h-screen m-0 p-0">
    <TopBar />
    <div class="flex-1 overflow-hidden">
        <CodeMirror 
            class="editor" 
            bind:value 
            lang={btmlSupport}
            theme={oneDark}
        />
    </div>
    <Footer />
</div>

<style>
    :global(.editor) {
        width: 100%;
        height: 100%;
    }
    
    :global(.cm-editor) {
        width: 100% !important;
        height: 100% !important;
    }
    
    :global(.cm-scroller) {
        height: 100% !important;
    }
</style>
