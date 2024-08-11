# Function Summary

## <div class='my-heading' style='color: darkgreen;'>qtdraw_app.py

### <div class='my-heading' style='color: royalblue;'>QtDraw

| Function | Summary |
|--------|----------|
| QtDraw | 3D drawing tool. |
| create_gui | create gui. |
| open_file | Open file dialog. |
| load_file | Load file. |
| save_file | Save file dialog. |
| save_screenshot | Save screenshot dialog. |
| create_panel | create right panel. |
| create_gui_unit_cell | Create unit cell panel. |
| create_gui_view | Create view panel. |
| create_gui_dataset | Create dataset panel. |
| create_gui_misc | Create misc. panel. |
| create_gui_debug | Create debug panel. |
| _update_panel | Update widget in panel. |
| _update_application | Update application sytle. |
| _update_title | Update window title. |
| _update_unit_cell | Update unit cell widget. |
| _update_view | Update view. |
| _set_crystal | Set crystal. |
| _set_origin | Set origin. |
| _set_a | Set lattice constant, a. |
| _set_b | Set lattice constant, b. |
| _set_c | Set lattice constant, c. |
| _set_alpha | Set lattice angle, alpha. |
| _set_beta | Set lattice angle, beta. |
| _set_gamma | Set lattice angle, gamma. |
| _set_clip | Set clip mode. |
| _set_repeat | Set repeat mode. |
| _set_bar | set bar. |
| _set_lower | Set lower bound. |
| _set_upper | set upper bound. |
| _set_view_default | set default. |
| _set_view | set view direction. |
| _set_parallel | set parallel projection mode. |
| _set_grid | set grid mode. |
| _set_axis_type | set axis type. |
| _set_cell_mode | set cell mode. |
| create_connection | Create connections. |
| _nonrepeat | Transform data into non-repeat data. |
| _show_preference | Show preference panel. |
| _show_about | Show about panel. |
| _show_multipie | Show MultiPie panel. |
| _show_status_data | Show status data dialog. |
| _show_preference_data | Show preference data dialog. |
| _show_actor_list | Show actor list dialog. |
| _show_raw_data | Show raw data dialog. |
| _show_camera_info | Show camera info. dialog. |
| _clear_data | Clear data (actor and data). |
| exec | Execute QtDraw. |
| closeEvent | Close with dialog. |
| close | Close dialogs. |
| update_status | Update status. |
| update_preference | Update preference. |
| write_info | Write text message into Info dialog. |
| add_site | Add site. |
| add_bond | Add bond. |
| add_vector | Add vector. |
| add_orbital | Add orbital. |
| add_stream | Add stream. |
| add_line | Add line. |
| add_plane | Add plane. |
| add_circle | Add circle. |
| add_torus | Add torus. |
| add_ellipsoid | Add ellipsoid. |
| add_toroid | Add toroid. |
| add_box | Add box. |
| add_polygon | Add polygon. |
| add_spline | Add spline. |
| add_spline_t | Add spline (parametric). |
| add_text3d | Add text 3d. |
| add_isosurface | Add isosurface. |
| add_caption | Add caption. |
| add_text2d | Add text 2d. |
| plot_orbital_from_data | Plot orbital from data. |
| plot_stream_from_data | Plot stream from data (vectors in cartesian coordinate). |
| set_unit_cell | Set unit cell. |
| set_crystal | Set crystal. |
| set_origin | Set origin. |
| set_clip | Set clip mode. |
| set_repeat | Set repeat mode. |
| nonrepeat_data | Transform data to non-repeat data. |
| set_range | Set cell range. |
| set_view | Set view point. |
| set_parallel_projection | Set parallel projection mode. |
| set_grid | Set grid mode. |
| set_bar | Set scalar bar mode. |
| set_axis | Set axis widget. |
| set_cell | Set unit cell. |
| add_mesh | Add any PyVista/VTK mesh or dataset that PyVista can wrap to the scene. |


## <div class='my-heading' style='color: darkgreen;'>dialog_about.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| get_version_info | Get version info. |


### <div class='my-heading' style='color: royalblue;'>AboutDialog

| Function | Summary |
|--------|----------|
| AboutDialog | About dialog. |
| create_about_panel | Create about panel. |


## <div class='my-heading' style='color: darkgreen;'>pyvista_widget.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| create_qtdraw_file | Create QtDraw file as background. |
| convert_qtdraw_v2 | Convert qtdraw file to version 2. |


### <div class='my-heading' style='color: royalblue;'>Window

| Function | Summary |
|--------|----------|
| Window | Window with logging. |


### <div class='my-heading' style='color: royalblue;'>PlotSignal

| Function | Summary |
|--------|----------|
| PlotSignal | For dict type of signal. |


### <div class='my-heading' style='color: royalblue;'>PyVistaWidget

| Function | Summary |
|--------|----------|
| PyVistaWidget | Widget for 3d plot layer using PyVista. |
| clear_info |  |
| set_additional_status | Set additional status. |
| add_site | Add site. |
| add_bond | Add bond. |
| add_vector | Add vector. |
| add_orbital | Add orbital. |
| add_stream | Add stream. |
| add_line | Add line. |
| add_plane | Add plane. |
| add_circle | Add circle. |
| add_torus | Add torus. |
| add_ellipsoid | Add ellipsoid. |
| add_toroid | Add toroid. |
| add_box | Add box. |
| add_polygon | Add polygon. |
| add_spline | Add spline. |
| add_spline_t | Add spline (parametric). |
| add_text3d | Add text 3d. |
| add_isosurface | Add isosurface. |
| add_caption | Add caption. |
| add_text2d | Add text 2d. |
| load | Load all info. |
| get_data_dict | Get data dict. |
| restore | Restore data and status from backup. |
| save_current | Save current data and stutus into self._backup. |
| save | save all info. |
| save_screenshot | Save screenshot to file. |
| write_info | Write text message (emit message signal). |
| set_property | Set status and preference. |
| update_status | Update status. |
| update_preference | Update preference. |
| reload | Reload data and draw object. |
| refresh | Refresh widget setting. |
| a1 | Get a1 unit vector. |
| a2 | Get a2 unit vector. |
| a3 | Get a3 unit vector. |
| origin | Get origin. |
| cell_volume | Get cell volume. |
| A_matrix | Get transform matrix. |
| A_matrix_norm | Get transform matrix (normalized). |
| G_matrix | Get metric matrix. |
| actor_list | Get list of actor. |
| window_title | Get window title. |
| copyright | Copyright string. |
| set_model | Set model name. |
| set_crystal | Set crystal. |
| set_origin | Set origin. |
| set_unit_cell | Set unit cell. |
| set_clip | Set clip mode. |
| hide_outside_actor | Hide actors outside the range. |
| show_outside_actor | Show actors outside the range. |
| set_repeat | Set repeat mode. |
| set_range | Set cell range. |
| set_view | Set view point. |
| set_parallel_projection | Set parallel projection mode. |
| set_grid | Set grid mode. |
| set_bar | Set scalar bar mode. |
| set_axis | Set axis widget. |
| set_cell | Set unit cell. |
| init_data_model | Initialize data model. |
| set_theme | Set pyvista theme. |
| show_cell | Show unit cell. |
| set_light | Set light. |
| set_latex | Set LaTeX environment. |
| screen_off | Screen off. |
| screen_on | Screen on. |
| get_camera_info | Get camera info. |
| set_camera_info | Get camera info. |
| add_data | Add data. |
| repeat_data | Repeat data. |
| nonrepeat_data | Transform data to non-repeat data. |
| set_actor | Set actor. |
| delete_actor | Remove actor. |
| change_check_state | Change check state (when name is off, label is also off). |
| open_tab_group_view | Open tab group view. |
| release_mouse | Release mouse button. |
| keyPressEvent | In order to prevent default keys. |
| closeEvent | In order to close QInteractor, and opened dialogs. |
| close | In order to close QInteractor, and opened dialogs. |
| remove_data | Remove data. |
| show_context_menu | Show context menu. |
| open_action | Action for open in context menum. |
| hide_action | Action for hide in context menu. |
| remove_action | Action for remove in context menu. |
| select_actor | Select actor with spotlight. |
| deselect_actor | Deselect actor with reset of spotlight. |
| deselect_actor_all | Deselect all selected actors. |
| change_selection | Change selection for spotlight. |
| find_index | Find index from actor. |
| set_common_row_data | Set common row data. |
| plot_data | Plot mesh from data. |
| redraw | Redraw all object. |
| common_option | Create common option to plot. |
| label_option | Create common option to plot. |
| check_hide | Check hide state. |
| plot_data_site | Plot site. |
| plot_data_bond | Plot bond. |
| plot_data_vector | Plot vector. |
| plot_data_orbital | Plot orbital. |
| plot_data_stream | Plot stream (vectors in cartesian coordinate). |
| plot_data_line | Plot line. |
| plot_data_plane | Plot plane. |
| plot_data_circle | Plot circle. |
| plot_data_torus | Plot torus. |
| plot_data_ellipsoid | Plot ellipsoid. |
| plot_data_toroid | Plot toroid. |
| plot_data_box | Plot box. |
| plot_data_polygon | Plot polygon. |
| plot_data_text3d | Plot text3d (view and offset in reduced coordinate). |
| plot_data_isosurface | Plot isosurface. |
| plot_data_spline | Plot spline. |
| plot_data_spline_t | Plot spline (parametric). |
| plot_data_caption | Plot caption. |
| plot_data_text2d | Plot text 2d. |
| plot_label | Plot label. |
| set_isosurface_data | Set isosurface data. |
| plot_orbital_from_data | Plot orbital from data. |
| plot_stream_from_data | Plot stream from data (vectors in cartesian coordinate). |


## <div class='my-heading' style='color: darkgreen;'>dialog_preference.py

### <div class='my-heading' style='color: royalblue;'>PreferenceDialog

| Function | Summary |
|--------|----------|
| PreferenceDialog | Preference dialog. |
| create_label_panel | Create label panel. |
| create_axis_panel | Create axis panel. |
| create_cell_panel | Create cell panel. |
| create_light_panel | Create light panel. |
| create_latex_panel | Create LaTeX panel. |
| create_general_panel | Create general panel. |
| accept | Accept change. |
| reject | Reject change. |
| apply | Apply change. |


## <div class='my-heading' style='color: darkgreen;'>validator.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| validator_int | Validator for int. |
| validator_float | Validator for float. |
| validator_sympy_float | Validator for sympy. |
| validator_sympy | Validator for sympy. |
| validator_ilist | Validator for int list. |
| validator_list | Validator for sympy list. |
| validator_site | Validator for site. |
| validator_bond | Validator for bond. |
| validator_site_bond | Validator for site or bond. |
| validator_vector_site_bond | Validator for vector on site or bond. |
| validator_orbital_site_bond | Validator for orbital on site or bond. |


## <div class='my-heading' style='color: darkgreen;'>group_model.py

### <div class='my-heading' style='color: royalblue;'>GroupModel

| Function | Summary |
|--------|----------|
| GroupModel | Group data model (2 layer parent-child tree model). |
| group_name | Group name. |
| header | Header label. |
| block_update_widget | Block update widget. |
| is_parent | Is parent index ? |
| update_check_state | Update check state data. |
| set_data | Set data from list data. |
| set_row_data | Set row data. |
| set_check | Set check state. |
| tolist | Convert to list. |
| emit_update_all | Emit update for all data. |
| find_item | Find item. |
| set_check_state | Set check state of row. |
| get_row_data | Get row data. |
| emit_update_data | Emit update data. |
| append_row | Append row. |
| remove_row | Remove row. |
| move_row | Move row. |
| action_copy_row | Slot for copy row action. |
| action_insert_row | Slot for insert row action. |
| action_remove_row | Slot for remove row action. |
| setData | Set data (override). |
| debug_data_changed | Debug for dataChanged signal. |
| debug_updata_data | Debug for updateData signal. |
| debug_item_tree | Debug for showing item tree. |
| show_index | Get raw index. |
| get_role_str | Get role string. |
| tolist_index | Row data for given index. |
| clear_data | Clear data with keeping header and column info. |


## <div class='my-heading' style='color: darkgreen;'>delegate.py

### <div class='my-heading' style='color: royalblue;'>Delegate

| Function | Summary |
|--------|----------|
| Delegate | Base delegate. |
| setEditorData | Set editor data. |
| setModelData | Set model data. |
| updateEditorGeometry | Update editor geometry. |
| paint | Paint cell. |


### <div class='my-heading' style='color: royalblue;'>ComboDelegate

| Function | Summary |
|--------|----------|
| ComboDelegate | Create delegate for Combo. |
| createEditor | Create combobox. |


### <div class='my-heading' style='color: royalblue;'>ColorDelegate

| Function | Summary |
|--------|----------|
| ColorDelegate | Create delegate for ColorSelector. |
| createEditor | Create color selector. |


### <div class='my-heading' style='color: royalblue;'>EditorDelegate

| Function | Summary |
|--------|----------|
| EditorDelegate | Create delegate for Editor. |
| createEditor | Create editor. |


## <div class='my-heading' style='color: darkgreen;'>message_box.py

### <div class='my-heading' style='color: royalblue;'>MessageBox

| Function | Summary |
|--------|----------|
| MessageBox | Message box. |


## <div class='my-heading' style='color: darkgreen;'>group_view.py

### <div class='my-heading' style='color: royalblue;'>GroupView

| Function | Summary |
|--------|----------|
| GroupView | Group view. |
| clear_selection | Clear selection. |
| mousePressEvent | Mouse press event for focus or clear selection. |
| keyPressEvent | Key press event for ESC and up and down keys. |
| context_menu | Context menu. |
| insert_row | Insert row. |
| copy_row | Copy row. |
| remove_row | Remove row. |
| update_widget | Update widget. |
| set_widget | Set widget. |
| selection_changed | For Selection changed. |
| select_row | Select row. |


## <div class='my-heading' style='color: darkgreen;'>custom_widget.py

### <div class='my-heading' style='color: royalblue;'>Layout

| Function | Summary |
|--------|----------|
| Layout | Layout widget. |


### <div class='my-heading' style='color: royalblue;'>Panel

| Function | Summary |
|--------|----------|
| Panel | Panel widget. |


### <div class='my-heading' style='color: royalblue;'>Color

| Function | Summary |
|--------|----------|
| Color | Color |


### <div class='my-heading' style='color: royalblue;'>Label

| Function | Summary |
|--------|----------|
| Label | Label widget. |
| setText | Set text. |


### <div class='my-heading' style='color: royalblue;'>ColorLabel

| Function | Summary |
|--------|----------|
| ColorLabel | Color label widget. |


### <div class='my-heading' style='color: royalblue;'>LineEdit

| Function | Summary |
|--------|----------|
| LineEdit | Line editor. |
| validator | Validator type. |
| read_only | Read only ? |
| close_edit | Close editor. |
| raw_text | Raw text. |
| setText | Set text. |
| set_validator | Set validator. |
| set_read_only | Set read only. |
| focusInEvent | Focus-out event. |
| focusOutEvent | Focus-out event. |
| clearFocus | Clear focus. |
| keyPressEvent | Key event. |


### <div class='my-heading' style='color: royalblue;'>HBar

| Function | Summary |
|--------|----------|
| HBar | Horizontal bar item. |


### <div class='my-heading' style='color: royalblue;'>Button

| Function | Summary |
|--------|----------|
| Button | Button widget. |


### <div class='my-heading' style='color: royalblue;'>Combo

| Function | Summary |
|--------|----------|
| Combo | Combo widget. |
| get_item | Get item. |
| set_item | Set item. |
| find_index | Find index. |


### <div class='my-heading' style='color: royalblue;'>Spin

| Function | Summary |
|--------|----------|
| Spin | Spin widget. |


### <div class='my-heading' style='color: royalblue;'>DSpin

| Function | Summary |
|--------|----------|
| DSpin | Spin widget. |


### <div class='my-heading' style='color: royalblue;'>Check

| Function | Summary |
|--------|----------|
| Check | Check widget. |
| is_checked | Is checked ? |


### <div class='my-heading' style='color: royalblue;'>VSpacer

| Function | Summary |
|--------|----------|
| VSpacer | Vertical spacer. |


### <div class='my-heading' style='color: royalblue;'>HSpacer

| Function | Summary |
|--------|----------|
| HSpacer | Horizontal spacer. |


### <div class='my-heading' style='color: royalblue;'>Editor

| Function | Summary |
|--------|----------|
| Editor | Math equation label widget. |
| close_editor | Close editor. |
| clearFocus | Clear focus. |
| mouseDoubleClickEvent | Mouse double-click event. |
| mousePressEvent | Mouse click event. |
| text | Text. |
| setText | Set text. |
| raw_text | Raw text. |
| setCurrentText | Set current text. |
| currentText | Get current text. |


### <div class='my-heading' style='color: royalblue;'>ColorSelector

| Function | Summary |
|--------|----------|
| ColorSelector | Color selector widget. |


## <div class='my-heading' style='color: darkgreen;'>table_view.py

### <div class='my-heading' style='color: royalblue;'>TableView

| Function | Summary |
|--------|----------|
| TableView | Table view (math). |


## <div class='my-heading' style='color: darkgreen;'>tab_group_view.py

### <div class='my-heading' style='color: royalblue;'>TabGroupView

| Function | Summary |
|--------|----------|
| TabGroupView | Data view group. |
| select_tab | Select tab. |
| closeEvent | Close event for deselect all. |


## <div class='my-heading' style='color: darkgreen;'>latex_to_png.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| latex_to_png | Render a LaTeX string to png via matplotlib. |


## <div class='my-heading' style='color: darkgreen;'>util_axis.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _create_label_axes_actor | Create label only orientation axes actor. |
| _create_axes_actor | Create custom axes actor. |
| create_axes_widget | Create axes widget. |
| create_unit_cell | Create unit cell mesh. |
| get_view_vector | Get view and viewup. |
| create_grid | Create grid point. |
| get_lattice_vector | Get lattice vector. |
| get_repeat_range | Get repeart range. |
| get_outside_box | Get indices outside range. |


## <div class='my-heading' style='color: darkgreen;'>latex_to_svg.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| latex_to_svg | Render a LaTeX string to svg via matplotlib. |
| get_svg_size | Get SVG size. |


### <div class='my-heading' style='color: royalblue;'>SVGWidget

| Function | Summary |
|--------|----------|
| paintEvent |  |


### <div class='my-heading' style='color: royalblue;'>MathText

| Function | Summary |
|--------|----------|
| MathText | Math Text via SVG. |


## <div class='my-heading' style='color: darkgreen;'>util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| check_get_site | Check and get site. |
| check_get_bond | Check and get bond. |
| check_get_site_bond | Check and get site (bond center) from site_bond. |
| create_samb_object | Create SAMB object. |
| check_linear_combination | Check form of linear combination. |
| combined_format | Create formatted combined SAMB. |
| parse_modulation_list | Parse modulation list. |


## <div class='my-heading' style='color: darkgreen;'>color_selector_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _colormap2pixmap | Convert colormap to pixmap. |
| _color2pixmap | Convert color/colormap to pixmap. |
| color2pixmap | Convert color/colormap to QPixmap. |


## <div class='my-heading' style='color: darkgreen;'>util_str.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| str_to_list | Convert a string to a list of strings. |
| is_regular_list | Is regular-shaped list ? |
| apply_to_list | Apply a function to each element of a list. |
| apply_to_numpy | Apply a function to each element of ndarray. |
| to_fraction | Convert a float number to a fractional one. |
| get_variable | Get variables used in a sympy expression. |
| str_to_sympy | Convert a string to a sympy. |
| str_to_numpy | Convert a string (list) to a numpy array. |
| affine_trans | Affine transformation, A.v + s. |


## <div class='my-heading' style='color: darkgreen;'>logging_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| timer | Timer decorater. |
| start_logging | Start logging. |
| wrapper |  |


### <div class='my-heading' style='color: royalblue;'>LogHandler

| Function | Summary |
|--------|----------|
| LogHandler | Log handler. |
| emit | Emit message. |


### <div class='my-heading' style='color: royalblue;'>LogWidget

| Function | Summary |
|--------|----------|
| LogWidget | Log widget. |
| append_text | Append text. |
| set_text | Set text. |
| clear | Clear log message. |
| save | Save log message. |


## <div class='my-heading' style='color: darkgreen;'>basic_object.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _str_poly_array | Convert from polynomial string to scalar array. |
| _str_vec_array | Convert from polynomial string (vector) to vector and scalar (abs.) arrays. |
| create_sphere | Create sphere object. |
| create_bond | Create bond object. |
| create_vector | Create vector object. |
| create_orbital | Create orbital object. |
| create_stream | Create steam vector object. |
| create_line | Create line object. |
| create_plane | Create plane object. |
| create_circle | Create circle object. |
| create_torus | Create torus object. |
| create_ellipsoid | Create ellipsoid object. |
| create_toroid | Create ellipsoid object. |
| create_box | Create box object. |
| create_polygon | Create polygon object. |
| create_text3d | Create text3d object. |
| create_spline | Create spline object. |
| create_spline_t | Create parametric spline object. |
| create_isosurface | Create isosurface. |
| create_orbital_data | Create orbital object from data. |
| create_stream_data | Create steam vector object. |


## <div class='my-heading' style='color: darkgreen;'>qt_event_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| gui_qt | Execute gui magic command for qtconsole. |
| get_qt_application | Get Qt application. |


### <div class='my-heading' style='color: royalblue;'>ExceptionHook

| Function | Summary |
|--------|----------|
| ExceptionHook | Exception hook. |
| hook | Callback for uncaught exceptions. |
| reset | Reset exception hook. |


## <div class='my-heading' style='color: darkgreen;'>pdf_viewer.py

### <div class='my-heading' style='color: royalblue;'>PDFViewer

| Function | Summary |
|--------|----------|
| PDFViewer | Simple PDF viewer. |
| load | Load PDF file. |
| save | Save PDF file (default = current directory). |
| set_title | Set window title. |


## <div class='my-heading' style='color: darkgreen;'>read_material.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| read_draw | Read and draw CIF, XSF, VESTA file. |


## <div class='my-heading' style='color: darkgreen;'>converter.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| to_bool | Convert from string to bool. |
| get_status | Get update status. |
| get_camera | Get camera info. |
| get_preference | Get update preference. |
| get_multipie | Get multipie info. |
| get_data | Get updated data. |
| convert_version2 | Converter from ver.1 to ver. 2. |


## <div class='my-heading' style='color: darkgreen;'>vesta.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| parse_vesta | parse VESTA file. |
| create_structure_vesta | create Structure from vesta dict. |


## <div class='my-heading' style='color: darkgreen;'>xsf.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| extract_data_xsf | Read xsf file (grid data part only). |
| create_data |  |


## <div class='my-heading' style='color: darkgreen;'>qtdraw.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| cmd | execute QtDraw. |


## <div class='my-heading' style='color: darkgreen;'>conv_qtdraw2.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| cmd | Convert QtDraw to version 2. |


## <div class='my-heading' style='color: darkgreen;'>plugin_multipie.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _mapping_str | Convert mapping No. to those start from one. |
| remove_latex |  |


### <div class='my-heading' style='color: royalblue;'>MultiPiePlugin

| Function | Summary |
|--------|----------|
| MultiPiePlugin | MultiPie plugin. |
| version | Version. |
| group | Group status dict. |
| obj | Object status dict. |
| basis | Basis status dict. |
| plus | Plus status dict. |
| counter | Counter number and increment. |
| clear_counter | Clear counter. |
| set_group | Set group and plus dict. |
| get_product_decomp | Set product decomposition. |
| get_harmonics_irrep | Get harmonics irrep. |
| get_harmonics | Get harmonics. |
| find_wyckoff | Find Wyckoff position. |
| add_equivalent_site | Add equivalent sites. |
| add_equivalent_bond | Add equivalent bonds. |
| add_vector_equivalent_site | Add vectors at equivalent sites. |
| add_orbital_equivalent_site | Add orbitals at equivalent sites. |
| create_combined | Create combined SAMB. |
| gen_site_samb | Generate site cluster SAMB. |
| gen_bond_samb | Generate bond cluster SAMB. |
| gen_vector_samb | Generate vector cluster SAMB. |
| gen_orbital_samb | Generate orbital cluster SAMB. |
| gen_hopping_samb | Generate hopping SAMB. |
| create_hopping_direction | Create normal bond direction. |
| add_site_samb | Add site cluster SAMB. |
| add_bond_samb | Add bond cluster SAMB. |
| add_vector_samb | Add vector cluster SAMB. |
| add_orbital_samb | Add orbital cluster SAMB. |
| add_vector_modulation | Add vector SAMB modulation. |
| add_orbital_modulation | Add orbitl SAMB modulation. |
| add_hopping_samb | Add normal hopping direction. |
| add_harmonics_set | Add harmonics set. |
| add_virtual_cluster | Add virtual cluster. |
| create_samb_modulation | Create SAMB modulation object. |
| create_phase_factor | Create phase factor. |


## <div class='my-heading' style='color: darkgreen;'>dialog_modulation.py

### <div class='my-heading' style='color: royalblue;'>ModulationDialog

| Function | Summary |
|--------|----------|
| ModulationDialog | Modulation dialog. |
| create_panel | Create panel. |
| get_raw_data | Get raw modulation list. |
| add_modulation | Add modulation. |
| add_data | Add data in panel. |
| remove_data | Remove data in panel. |
| accept | Accept input. |
| reject | Reject input. |
| apply | Apply input. |
| close | Close. |


## <div class='my-heading' style='color: darkgreen;'>dialog_info.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| show_group_info | Show group info. |
| show_symmetry_operation | Show symmetry operation panel. |
| show_character_table | Show character table panel. |
| show_wyckoff | Show Wyckoff position panel. |
| show_product_table | Show product table panel. |
| show_harmonics | Show harmonics panel. |
| show_harmonics_decomp | Show harmonics decomposition panel. |
| show_virtual_cluster | Show virtual cluster panel. |
| show_atomic_multipole | Show atomic multipole panel. |
| show_response | Show response tensor panel. |


### <div class='my-heading' style='color: royalblue;'>InfoPanel

| Function | Summary |
|--------|----------|
| InfoPanel | Info panel. |


## <div class='my-heading' style='color: darkgreen;'>dialog_multipie.py

### <div class='my-heading' style='color: royalblue;'>MultiPieDialog

| Function | Summary |
|--------|----------|
| MultiPieDialog | MultiPie dialog. |
| group | Group status dict. |
| obj | Object status dict. |
| basis | Basis status dict. |
| plus | Plus status dict. |
| set_group_panel_value | Set initial values in group panel. |
| set_object_panel_value | Set initial values in object panel. |
| set_basis_panel_value | Set initial values in basis panel. |
| create_sub_group_panel | Create subgroup panel. |
| create_group_panel | Create group panel. |
| create_object_panel | Create object panel. |
| create_basis_panel | Create basis panel. |
| set_group_connection | Set connections in group panel. |
| set_object_connection | Set connections in object panel. |
| set_basis_connection | Set connections in basis panel. |
| set_group_item | Set group widgets. |
| set_irrep_item | Set irrep widgets. |
| set_wyckoff_item | Set Wyckoff list. |
| set_basis_item | Set basis widgets. |
| set_harmonics_item | Set harmonics widgets. |
| set_group_type | Set group type. |
| set_crystal_type | Set crystal type. |
| set_group | Set current group. |
| set_irrep_decomp | Set decomposition of product of irreps. |
| set_harmonics_type | Set harmonics type. |
| set_harmonics_rank | Set harmonics rank. |
| set_harmonics_decomp | Set harmonics decomposition. |
| set_vc_wyckoff | Set wyckoff in virtual cluster. |
| set_vc_neighbor | Set neighbor list in virtual cluster. |
| set_atomic_type | Set atomic multipole type. |
| set_atomic_basis_type | Set atomic multipole basis type. |
| set_atomic_bra_ket | Set bra and ket basis of atomic multipole. |
| set_response_type | Set type of response tensor. |
| set_response_rank | Set rank of response tensor. |
| set_obj_vector_type | Set vector type in object panel. |
| set_obj_orbital_type | Set orbital type in object panel. |
| set_obj_harmonics_type | Set harmonics type in object panel. |
| set_obj_harmonics_rank | Set harmonics rank in object panel. |
| set_obj_harmonics | Set harmonics in object panel. |
| set_obj_wyckoff | Set Wyckoff position in object panel. |
| show_symmetry_operation | Show symmetry operation panel. |
| show_character_table | Show character table panel. |
| show_wyckoff | Show Wyckoff position panel. |
| show_product_table | Show product table panel. |
| show_harmonics | Show harmonics panel. |
| show_harmonics_decomp | Show harmonics decomposition panel. |
| show_virtual_cluster | Show virtual cluster panel. |
| show_atomic | Show atomic multipole panel. |
| show_response | Show response tensor panel. |
| obj_add_site | Add representative site in object dict. |
| obj_add_bond | Add representative bond in object dict. |
| obj_add_vector | Add equivalent vectors in object dict. |
| obj_add_orbital | Add equivalent orbitals in object dict. |
| obj_add_harmonics | Add equivalent poing-group harmonics in object dict. |
| basis_gen_site | Generate site cluster SAMB. |
| basis_set_site_select | Set site cluster SAMB selection list. |
| basis_add_site | Add site cluster SAMB. |
| basis_gen_bond | Generate bond cluster SAMB. |
| basis_set_bond_select | Set bond cluster SAMB selection list. |
| basis_add_bond | Add bond cluster SAMB. |
| basis_gen_vector | Generate vector cluster SAMB. |
| basis_set_vector_select | Set vector cluster SAMB selection list. |
| basis_add_vector | Add vector cluster SAMB. |
| basis_add_vector_lc | Add linear combination of vector cluster SAMB. |
| basis_gen_vector_modulation | Generate vector modulation. |
| basis_gen_orbital | Generate orbital cluster SAMB. |
| basis_set_orbital_select | Set orbital cluster SAMB selection list. |
| basis_add_orbital | Add orbital cluster SAMB. |
| basis_add_orbital_lc | Add linear combination of orbital cluster SAMB. |
| basis_gen_orbital_modulation | Generate orbital modulation. |
| basis_add_hopping | Add hopping SAMB. |
| close | Close dialogs. |


