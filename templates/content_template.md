
## `rir:Calendar2`{{ heading }}
{{ content }}

```dataviewjs
// Filter pages by date match
const pages = dv.pages('"Movies & TV Shows"').where(p => p.watched && String(p.watched).substring(0, 10) === dv.current().file.name.substring(0, 10));

// Calculate the total length in minutes
const totalLength = pages.values.reduce((sum, p) => sum + p.length, 0);

// Convert total length to hours and minutes
const hours = Math.floor(totalLength / 60);
const minutes = totalLength % 60;

if (pages.values.length > 0) {
    dv.el("div", "<hr>"); // Add a horizontal line
    dv.header(6, "Today I watched");
    dv.list(pages.values.map(p => dv.fileLink(p.file.path)));

    // Display the total time as hours and minutes
    dv.paragraph(`Total time watched: ${hours} hours and ${minutes} minutes`);
}
```
---
{{ location }} tag:note