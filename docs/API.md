<img width="128" src="qtdraw_logo.png">

# QtDraw

API for drawing objects.

## Site (sphere)

**plot_site(position, size=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot site (reduced).
- **size** (float, optional): size of site.
- **color** (str, optional): color of site.
- **opacity** (float, optional): opacity of site.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.

## Bond

**plot_bond(position, vector=None, width=None, color=None, color2="", opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot bond center (reduced).
- **vector** (str or list or ndarray or NSArray, optional): bond vector (reduced).
- **width** (float, optional): width of bond.
- **color** (str, optional): color of bond.
- **color2** (str, optional): color of bond for half tail.
- **opacity** (float, optional): opacity of bond.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.
- if color2 is "", same color is used.

## Vector

**plot_vector(position, vector=None, length=None, width=None, offset=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot vector (reduced).
- **vector** (str or list or ndarray or NSArray, optional): vector direction (cartesian).
- **length** (float, optional): length of vector.
- **width** (float, optional): width of vector.
- **offset** (float, optional): offset of vector end (ratio).
- **color** (str, optional): color of vector.
- **opacity** (float, optional): opacity of vector.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.
- vector is not necessary to be normalized.

## Orbital

**plot_orbital(position, shape=None, surface="", size=None, theta_range=None, phi_range=None, color=None, opacity=None, space=None, scale=True, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot orbital (reduced).
- **shape** (str, optional): (x,y,z) shape of orbital in terms of (x,y,z) (cartesian).
- **surface** (str, optional): surface color in terms of (x,y,z) (cartesian).
- **size** (float, optional): size of orbital.
- **theta_range** (str or list or ndarray or NSArray, optional): theta range, default=[0,180].
- **phi_range** (str or list or ndarray or NSArray, optional): phi range, default=[0,360].
- **color** (str, optional): color/colormap of surface.
- **opacity** (float, optional): opacity of orbital.
- **space** (int, optional): pre-space of label.
- **scale** (bool, optional): if False, absolute size is used.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if surface is "", surface is same as shape.
- if argument is None, default value is used.

## Stream vector with center orbital

**plot_stream_vector(position, shape=None, vector=None, size=None, v_size=None, width=None, scale=None, theta=None, phi=None, theta_range=None, phi_range=None, color=None, component=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot stream vector (reduced).
- **shape** (str, optional): shape of center orbital in terms of (x,y,z) (cartesian).
- **vector** (str or list or ndarray or NSArray, optional): vector components in terms of (x,y,z) [str]/str (cartesian).
- **size** (float, optional): size of orbital.
- **v_size** (float, optional): ratio of vector size to orbital.
- **width** (float, optional): width of vector.
- **scale** (bool, optional): scale vector size by value ?
- **theta** (int, optional): resolution in theta direction.
- **phi** (int, optional): resolution in phi direction.
- **theta_range** (str or list or ndarray or NSArray, optional): theta range, default=[0,180].
- **phi_range** (str or list or ndarray or NSArray, optional): phi range, default=[0,360].
- **color** (str, optional): color of vector.
- **component** (int, optional): component of vector to use for colormap (0,1,2,None = x,y,z,abs.).
- **opacity** (float, optional): opacity of center orbital.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if shape is None, "1" is used.
- if argument is None, default value is used.

## Plane

**plot_plane(position, normal=None, x=None, y=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot plane (reduced).
- **normal** (str or list or ndarray or NSArray, optional): normal vector of plane (reduced).
- **x** (float, optional): x size of plane.
- **y** (float, optional); y size of plane.
- **color** (str, optional): color of plane.
- **opacity** (float, optional): opacity of plane.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- position is for center of plane.
- if argument is None, default value is used.
- normal is not necessary to be normalized.

## Box

**plot_box(position, a1=None, a2=None, a3=None, edge=None, wireframe=None, width=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot box (reduced).
- **a1** (str or list or ndarray or NSArray, optional): 1st direction of box (reduced).
- **a2** (str or list or ndarray or NSArray, optional): 2nd direction of box (reduced).
- **a3** (str or list or ndarray or NSArray, optional): 3rd direction of box (reduced).
- **edge** (bool, optional): show edge of box ?
- **wireframe** (bool, optional): draw box by wireframe ?
- **width** (float, optional): line width of box for wireframe plot.
- **color** (str, optional): color of box.
- **opacity** (float, optional): opacity of box.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.

## Polygon

**plot_polygon(position, point=None, connection=None, edge=None, wireframe=None, width=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot polygon (reduced).
- **point** (str or list or ndarray or NSArray, optional): vertices of polygon (reduced).
- **connection** (str or list or ndarray or NSArray, optional): list of connected vectices for each plane.
- **edge** (bool, optional): show edge of box ?
- **wireframe** (bool, optional): draw box by wireframe ?
- **width** (float, optional): line width of box for wireframe plot.
- **color** (str, optional): color of box.
- **opacity** (float, optional): opacity of box.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.

## 3d text
**plot_text3d(position, text=None, size=None, depth=None, normal=None, offset=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot 3d text (reduced).
- **text** (str, optional): text.
- **size** (float, optional): size of text.
- **depth** (float, optional): depth of text.
- **normal** (str or list or ndarray or NSArray, optional): normal vector of text (reduced).
- **offset** (str or list or ndarray or NSArray, optional): offset of text.
- **color** (str, optional): color of text.
- **opacity** (float, optional): opacity of text.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.
- normal is not necessary to be normalized.

## Spline curve

**plot_spline(position, point=None, width=None, n_interp=None, closed=None, natural=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot spline curve (reduced).
- **point** (str or list or ndarray or NSArray, optional): points to be interpolated (reduced).
- **width** (float, optioanl): width of spline curve.
- **n_interp** (int, optional): number of interpolation points.
- **closed** (bool, optional): closed spline ?
- **natural** (bool, optional): natural boundary ?
- **color** (str, optional): color of spline curve.
- **opacity** (float, optional): opacity of spline curve.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.

## Spline curve (parametric function)

**plot_spline_t(position, expression=None, t_range=None, width=None, n_interp=None, closed=None, natural=None, color=None, opacity=None, space=None, name=None, label="", show_lbl=False)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot spline curve (reduced).
- **expression** (str or list or ndarray or NSArray, optional): component function of "t" to create interpolated points (reduced).
- **t_range** (str or list or ndarray or NSArray, optional): range of "t", [start, stop, step].
- **width** (float, optioanl): width of spline curve.
- **n_interp** (int, optional): number of interpolation points.
- **closed** (bool, optional): closed spline ?
- **natural** (bool, optional): natural boundary ?
- **color** (str, optional): color of spline curve.
- **opacity** (float, optional): opacity of spline curve.
- **space** (int, optional): pre-space of label.
- **name** (str, optional): group name of object.
- **label** (str, optional): label of object.
- **show_lbl** (bool, optional): show label ?

Notes:
- if argument is None, default value is used.

## Caption

**plot_caption(position, caption=None, space=None, size=None, color=None, bold=None, name=None)**

Args:
- **position** (str or list or ndarray or NSArray): position(s) to plot labels (reduced).
- **caption** (str or list, optional): label or list of labels.
- **space** (int, optional): pre-space of label.
- **size** (int, optional): font size.
- **color** (str, optional): text color.
- **bold** (bool, optional): bold face ?
- **name** (str, optional): group name.

Notes:
- if caption is None, simple number is used.
- if argument is None, default value is used.
- list size of caption must be equal to that of position.

## Text

**plot_text(position, caption=None, relative=None, size=None, color=None, font=None, name=None)**

Args:
- **position** (str or list or ndarray or NSArray): position to plot caption, [x,y].
- **caption** (str, optional): label.
- **relative** (bool, optional): relative position ?
- **size** (int, optional): font size.
- **color** (str, optional): text color.
- **font** (str, optional): font, "arial/times/courier".
- **name** (str, optional): group name.

Notes:
- if argument is None, default value is used.
