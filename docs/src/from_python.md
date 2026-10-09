# Usage from Python code

**QtDraw** and **PyVistaWidget** can be used from Python code.
The following API is avalilable to draw objects.

## Undo and redo

`QtDraw` keeps the history of the document (objects, unit cell, range and MultiPie group) as the `Edit` menu does.
`undo()` and `redo()` move in this history, and `can_undo()` and `can_redo()` tell whether they can.

```python
qtdraw.add_site(name="A")
qtdraw.add_bond(name="B")  # the same cell: one step together with the site.
qtdraw.undo()  # removes both.
```

A change is recorded when the event loop runs after it, so the calls in one Jupyter cell or in one function are one step.
If the calls run the event loop themselves (e.g. a dialog or `processEvents()`), they may be split into several steps.
`PyVistaWidget` used alone has no history.

## API in QtDraw

```{eval-rst}
.. autoclass:: qtdraw.core.qtdraw_app.QtDraw
   :members:
   :exclude-members: staticMetaObject
```

## API in PyVistaWidget

```{eval-rst}
.. autoclass:: qtdraw.core.pyvista_widget.PyVistaWidget
   :members:
   :exclude-members: staticMetaObject
```
