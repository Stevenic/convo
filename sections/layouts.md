# Layout Sections

## Sidebar Layout

This layout add's a collapsible sidebar to a main content area.  You can style the sidebar by adding Style section like shown.   

```
Section: Layout
Create a sidebar on the left side of the screen.
Inside the sidebar, place a title aligned to the left and a toggle button aligned to the right.
When the sidebar is closed, hide the title & sidebar contents, and dock the toggle button to the far left of the screen. Leave enough space for the sidebar to be re-opened.

Create a main content area to the right of the sidebar.
Make sure the main content area takes the remaining space on the screen.

Section: Behavior
To toggle the sidebar:
    If the sidebar is open, then close it:
        Hide the title.
        Dock the toggle button to the far left of the screen, pointing right.
    Otherwise, open the sidebar:
        Show the title.
        Move the toggle button to the right side of the sidebar, pointing left.

Section: Style
Apply a "light mode" theme that's inspired by bootstrap.
Use a chevron for the sidebar toggle button.
```

