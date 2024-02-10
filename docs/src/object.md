# Objects

QtDraw can draw the following 3D objects.

- sphere (site)
- bond
- vector
- atomic orbital
- stream vector
- plane
- box
- polygon
- text (3d, 2d)
- spline curve by data or parametric function
- caption

To draw these objects, push `list` button in DataSet panel, and then push `Add` and input a group name. Properties of an object are editable by double click of each column.

These objects are also drawn from Python code.
See [API](api.md) for detail.

Example of all objects is found in [sample.qtdw](sample.qtdw), which is drawn by the following code:
```{literalinclude} sample.py
```
