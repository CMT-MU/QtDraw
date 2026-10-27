# Function Summary

## <div class='my-heading' style='color: darkgreen;'>qtdraw_app.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| add_extension | Add extension to file name if it does not have it. |
| settings | Settings of QtDraw kept between sessions, e.g. recent files. |
| help_text | Mouse and key operations. |
| action |  |
| choice |  |
| read |  |


### <div class='my-heading' style='color: royalblue;'>QtDraw

| Function | Summary |
|--------|----------|
| QtDraw | 3D drawing tool. |
| create_gui | create gui. |
| _create_menu | Create menu bar with standard shortcuts. |
| _create_view_menu | Create view menu, following the view panel (the panel keeps the state). |
| _recent_files | Recent files, most recent first. |
| _add_recent_file | Add a file to the recent files. |
| _update_recent_menu | Fill File > Open Recent with existing recent files. |
| _open_recent | Open a recent file. |
| _set_tool_tips | Set tool tips of buttons. |
| _show_help | Show mouse and key operations. |
| open_file | Open file dialog. |
| load_file | Load file. |
| _update_panel_quietly | Update panel without applying its values to the document again. |
| save_file | Save to the file opened or saved last, or ask for a file name. |
| save_file_as | Save file dialog. |
| _loaded_from | Remember a loaded file: Save writes to a QtDraw file, but never to a material file. |
| _saved_to | Mark the document saved to a file, which Save writes from now on. |
| _save_screenshot | Save screenshot dialog. |
| create_panel | create right panel. |
| create_gui_unit_cell | Create unit cell panel. |
| create_gui_view | Create view panel. |
| create_gui_buttons | Create button panel (other commands are in the menu bar). |
| _document_state | Current document state to detect unsaved changes. |
| is_modified | Is document modified after it was opened or saved ? |
| _mark_saved | Mark current document as saved. |
| _create_modified_check | Update "*" in window title shortly after objects are changed. |
| _document_changed | Start the timer to record the document after a change. |
| _show_axis_cell | Show the axis and cell display in effect in the panel and the View menu, without applying it again. |
| _settle | Record the settled document for undo, and update the title. |
| _flush | Record a pending change now (before undo, redo, load, save and checking for unsaved changes). |
| _reset_history | Start a new undo history with the current document. |
| _update_undo_actions | Enable undo and redo in Edit menu. |
| _move_history | Undo (step=-1) or redo (step=1). |
| _restore | Restore a snapshot, or the current document again if it fails. |
| _after_restore | Update panel and MultiPie dialog after a restore. |
| undo | Undo the last change of the document (objects, unit cell, range and MultiPie). |
| redo | Redo the change undone last. |
| can_undo | Undo possible ? |
| can_redo | Redo possible ? |
| _commit_pending_input | Apply value typed in focused field but not confirmed by Enter. |
| _confirm_unsaved | Ask to save unsaved changes. |
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
| set_view_index |  |
| _nonrepeat | Transform data into non-repeat data. |
| _show_preference | Show preference panel. |
| _show_about | Show about panel. |
| _show_multipie | Show MultiPie panel, or offer to install MultiPie. |
| _install_multipie | Install MultiPie with pip in the background, showing its output in the Log window. |
| _multipie_installed | Use MultiPie after its installation, or tell why it failed. |
| _show_data_view | Show a window with internal data (Window menu), refreshed each time it is shown. |
| _status_text | Status data. |
| _preference_text | Preference data. |
| _actor_text | Actor names. |
| _raw_data_text | Raw data of all objects. |
| _camera_text | Camera info. |
| _clear_data | Clear data (actor and data). |
| clear_data | Clear data (actor and data). |
| exec | Execute QtDraw. |
| closeEvent | Close, asking to save unsaved changes. |
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
| set_model | Set model name. |
| set_unit_cell | Set unit cell. |
| set_crystal | Set crystal. |
| set_origin | Set origin. |
| set_clip | Set clip mode. |
| set_repeat | Set repeat mode. |
| set_nonrepeat | Transform data to non-repeat data. |
| set_range | Set cell range. |
| set_view | Set view point. |
| set_parallel_projection | Set parallel projection mode. |
| set_grid | Set grid mode. |
| set_bar | Set scalar bar mode. |
| set_axis | Set axis widget. |
| set_cell | Set unit cell. |
| add_mesh | Add any PyVista/VTK mesh or dataset that PyVista can wrap to the scene. |
| remove_actor | Remove actor. |
| load | Load all info. |
| save | save all info. |
| _save | Save the document, and keep the history valid in the new directory. |
| _check_multipie |  |
| mp_set_group | MultiPie: Set group. |
| mp_add_site | MultiPie: Add equivalent sites. |
| mp_add_bond | MultiPie: Add equivalent bonds. |
| mp_add_vector | MultiPie: Add transformed vectors at equivalent sites or bonds. |
| mp_add_orbital | MultiPie: Add transformed orbitals at equivalent sites or bonds. |
| mp_add_bond_definition | MultiPie: Create bond definition. |
| mp_site_samb_list | MultiPie: Create site SAMB list. |
| mp_add_site_samb | MultiPie: Add site SAMB. |
| mp_bond_samb_list | MultiPie: Create bond SAMB list. |
| mp_add_bond_samb | MultiPie: Add bond SAMB. |
| mp_vector_samb_list | MultiPie: Create vector SAMB list. |
| mp_add_vector_samb | MultiPie: Add vector SAMB. |
| mp_add_vector_samb_modulation | MultiPie: Add vector SAMB with modulation. |
| mp_orbital_samb_list | MultiPie: Create orbital SAMB. |
| mp_add_orbital_samb | MultiPie: Add orbital SAMB. |
| mp_add_orbital_samb_modulation | MultiPie: Add orbital SAMB with modulation. |


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
| convert_to_str | Convert from object to str, and remove spaces. |
| get_data_range |  |
| _literal_list | A list of plain numbers read without sympy, None if it is not one. |
| _parse_float | Parse a string of a list of numbers or expressions to floats (plain numbers without sympy, which is slow). |
| _parse_int | Parse a string of a list of integers or expressions to integers (truncated exactly, as sympy does). |
| _parse_cached_clear | Clear the cache of parsed strings. |
| _parse_cache_size | Number of cached strings. |
| _parse_vector | Parse a string of a list of numbers or expressions to a new array. |
| convert_str_vector | Convert 3-component vector(s) to A.(position+cell). |
| _caption_labels | Labels of a caption, one for each position. |
| split_filename | Split file name. |
| relative_path | Relative path, also to a directory outside start. |
| cat_filename | Cat filename. |
| format_text | Format Python text by black command if available. |
| write_text_atomic | Write text to file atomically (the old file is kept if writing fails). |
| _site_sphere | Sphere for site, shared by sites of the same size. |
| _suppress_stderr | Suppress output to stderr (file descriptor 2) of VTK and Qt, and restore it afterwards. |
| _batched | Decorator: run a method in a batch, rendering once at its end (see PyVistaWidget._batch_render). |
| isosurface_rename | New names of isosurface data files, relative to a new directory. |
| same_snapshot | Are two document snapshots the same ? |
| create_qtdraw_file | Create QtDraw file as background. |
| convert_qtdraw_v3 | Convert qtdraw file to version 3. |
| wrapper |  |
| set_light_prop |  |
| is_object |  |


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
| render | Render, or only note the request while a batch of changes is made (see _batch_render). |
| _batch_render | Make a batch of changes, rendering once at its end instead of once for each object. |
| actors | Access to renderer.actors. |
| clear_info | Clear info. |
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
| _set_loaded_data | Set loaded data. |
| document_snapshot | Snapshot of the document for undo. |
| rebase_snapshot | Snapshot whose isosurface data file names are relative to a new directory, as save() does. |
| restore_document | Restore a document snapshot (camera, view settings and preferences are kept). |
| _get_current_state | Get current state to restore it when loading fails. |
| _set_current_state | Set state obtained by _get_current_state. |
| get_data_dict | Get data dict. |
| restore | Restore data and status from backup. |
| save_current | Save current data and stutus into self._backup. |
| save | save all info. |
| _rebase_isosurface_data | Make isosurface data file names relative to a new directory. |
| save_screenshot | Save screenshot to file. |
| write_info | Write text message (emit message signal). |
| set_property | Set status and preference. |
| update_status | Update status. |
| update_preference | Update preference. |
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
| _caption_outside | Are all positions of a caption outside the range ? |
| clip_actor | Clip actor. |
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
| clear_data | Clear Data. |
| _clear_rows | Clear all rows (isosurface data is kept). |
| _remove_object_actors | Remove actors of all objects and their labels at once. |
| get_camera_info | Get camera info. |
| set_camera_info | Get camera info. |
| _set_default_zoom | Set default zoom. |
| add_data | Add data. |
| repeat_data | Repeat data. |
| set_nonrepeat | Transform data to non-repeat data. |
| nonrepeat_data | Transform data to non-repeat data. |
| set_actor | Set actor. |
| delete_actor | Remove actor. |
| change_check_state | Change check state (when name is off, label is also off). |
| open_tab_group_view | Open tab group view. |
| release_mouse | Release mouse button. |
| keyPressEvent | In order to prevent default keys. |
| closeEvent | In order to close QInteractor, and opened dialogs. |
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
| _not_drawn | Tell that an object is not drawn, and remove the object drawn before an edit. |
| _tips_left_out | Tell that arrow tips of an object are not drawn. |
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
| document_dir | Directory that data file names of the drawing are relative to. |
| set_isosurface_data | Set isosurface data. |
| plot_orbital_from_data | Plot orbital from data. |
| plot_stream_from_data | Plot stream from data (vectors in cartesian coordinate). |
| mp_set_group | MultiPie: Set group or group status. |
| _mp_set_group | MultiPie: Set group or group status. |
| mp_add_site | MultiPie: Add equivalent sites. |
| mp_add_bond | MultiPie: Add equivalent bonds. |
| mp_add_vector | MultiPie: Add transformed vectors at equivalent sites or bonds. |
| mp_add_orbital | MultiPie: Add transformed orbitals at equivalent sites or bonds. |
| mp_add_bond_definition | MultiPie: Create bond definition. |
| mp_site_samb_list | MultiPie: Create site SAMB list. |
| mp_add_site_samb | MultiPie: Add site SAMB. |
| mp_bond_samb_list | MultiPie: Create bond SAMB list. |
| mp_add_bond_samb | MultiPie: Add bond SAMB. |
| mp_vector_samb_list | MultiPie: Create vector SAMB list. |
| mp_add_vector_samb | MultiPie: Add vector SAMB. |
| mp_add_vector_samb_modulation | MultiPie: Add vector SAMB with modulation. |
| mp_orbital_samb_list | MultiPie: Create orbital SAMB. |
| mp_add_orbital_samb | MultiPie: Add orbital SAMB. |
| mp_add_orbital_samb_modulation | MultiPie: Add orbital SAMB with modulation. |


## <div class='my-heading' style='color: darkgreen;'>dialog_preference.py

### <div class='my-heading' style='color: royalblue;'>PreferenceDialog

| Function | Summary |
|--------|----------|
| PreferenceDialog | Preference dialog. |
| create_label_panel | Create label panel. |
| create_axis_panel | Create axis panel. |
| create_cell_panel | Create cell panel. |
| create_light_panel | Create light panel. |
| create_general_panel | Create general panel. |
| apply | Apply change. |


## <div class='my-heading' style='color: darkgreen;'>undo_history.py

### <div class='my-heading' style='color: royalblue;'>UndoHistory

| Function | Summary |
|--------|----------|
| UndoHistory | Undo history. |
| reset | Start a new history. |
| clear | Empty the history. |
| current | Snapshot at the current position. |
| record | Record a snapshot after the current position. |
| map | Replace every snapshot by func(snapshot), keeping the position. |
| can_undo | Undo possible ? |
| can_redo | Redo possible ? |
| peek_undo | Snapshot that undo restores (no move), None if not possible. |
| peek_redo | Snapshot that redo restores (no move), None if not possible. |
| commit_undo | Move the position back by one (after a successful restore). |
| commit_redo | Move the position forward by one (after a successful restore). |


## <div class='my-heading' style='color: darkgreen;'>validator.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| check_symbol | Check symbol. |
| _flat | Elements of a (nested, possibly ragged) list or array. |
| _format | Text of a (nested, possibly ragged) list or array, with each element formatted by fmt. |
| _finite_floats | Floats of numbers, None if one is not a finite real number (e.g. nan, oo or I). |
| _finite_complex | Complex numbers of numbers, None if one is not a finite number (e.g. nan or zoo). |
| _integers | Integers of numbers, None if one is not an integer fitting in 64 bits. |
| convert_to_bond | Convert to bond from str. |
| validator_int | Validator for int. |
| validator_float | Validator for float. |
| validator_list_float | Validator for list float. |
| validator_list_int | Validator for list int. |
| validator_math | Validator for math to LaTeX. |
| validator_site | Validator for site. |
| validator_bond | Validator for bond. |
| validator_site_bond | Validator for site or bond. |
| validator_vector_site_bond | Validator for vector on site or bond. |
| validator_orbital_site_bond | Validator for orbital on site or bond. |
| validator_hint | Explanation of accepted input for validator (used as tooltip). |
| fmt |  |
| value_range |  |
| shape_text |  |
| variables |  |


## <div class='my-heading' style='color: darkgreen;'>group_model.py

### <div class='my-heading' style='color: royalblue;'>GroupModel

| Function | Summary |
|--------|----------|
| GroupModel | Group data model (2 layer parent-child tree model). |
| group_name | Group name. |
| header | Header label. |
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
| _remove_row | Remove row. |
| _run_rename | Run a deferred rename once. |
| run_pending_renames | Run deferred group renames now. |
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


## <div class='my-heading' style='color: darkgreen;'>mathjax.py

### <div class='my-heading' style='color: royalblue;'>MathJaxSVG

| Function | Summary |
|--------|----------|
| MathJaxSVG | MathJax converter. |
| available | Is MathJax available ? |
| _thread_main |  |
| convert | Convert latex to SVG string. |
| _convert_plain | Convert latex to SVG string as plain text (when MathJax is not available). |
| close |  |
| _save_cache | Write memory cache to disk cache (a file that cannot be written is skipped). |
| _read_cache_file | Read a cache file. |
| _write_cache_file | Write a cache file atomically, so that another process never reads a partly written file. |
| _get_cache_path |  |
| _get_attribute |  |
| _replace_attribute |  |
| _flatten_svg_string |  |


### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| unwrap_inner_svg |  |


## <div class='my-heading' style='color: darkgreen;'>color_palette.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| name_sep |  |
| _rgb2html | convert RGB color to hex code (#??????). |
| _hex2rgb | convert hex (#??????) code to RGB. |
| custom_colormap | custom colormap. |
| check_color | check if name is color or colormap. |


## <div class='my-heading' style='color: darkgreen;'>color_selector_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _colormap2pixmap | Convert colormap to pixmap. |
| _color2pixmap | Convert color/colormap to pixmap. |
| color2pixmap | Convert color/colormap to QPixmap. |
| color_palette | Color pallete. |


## <div class='my-heading' style='color: darkgreen;'>delegate.py

### <div class='my-heading' style='color: royalblue;'>Delegate

| Function | Summary |
|--------|----------|
| Delegate |  |
| setEditorData |  |
| setModelData |  |
| paint |  |


### <div class='my-heading' style='color: royalblue;'>ComboDelegate

| Function | Summary |
|--------|----------|
| ComboDelegate |  |
| createEditor |  |
| updateEditorGeometry |  |
| sizeHint |  |


### <div class='my-heading' style='color: royalblue;'>ColorDelegate

| Function | Summary |
|--------|----------|
| ColorDelegate |  |
| createEditor |  |
| updateEditorGeometry |  |
| sizeHint |  |


### <div class='my-heading' style='color: royalblue;'>EditorDelegate

| Function | Summary |
|--------|----------|
| EditorDelegate |  |
| createEditor |  |
| _set_data_size |  |
| updateEditorGeometry |  |
| sizeHint |  |


## <div class='my-heading' style='color: darkgreen;'>logging_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| start_logging | Start logging. |


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


## <div class='my-heading' style='color: darkgreen;'>message_box.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| show_error | Show an error with a short message, and the full details behind "Show Details...". |


### <div class='my-heading' style='color: royalblue;'>MessageBox

| Function | Summary |
|--------|----------|
| MessageBox | Message box. |


### <div class='my-heading' style='color: royalblue;'>ResizableMessageBox

| Function | Summary |
|--------|----------|
| ResizableMessageBox |  |
| event | Lift the fixed size that QMessageBox sets again whenever it is laid out. |
| _unfill_screen | Give the box its size again if it fills the screen, but keep any other size, e.g. set by the user. |
| _lift_fixed_size | Allow any size, and let the details grow with the box. |


## <div class='my-heading' style='color: darkgreen;'>group_view.py

### <div class='my-heading' style='color: royalblue;'>GroupView

| Function | Summary |
|--------|----------|
| GroupView | Group view. |
| update_widget |  |
| force_refresh_widgets |  |
| _do_force_refresh |  |
| _open_editors_for_row |  |
| set_widget | Set widget. |
| clear_selection | Clear selection. |
| mousePressEvent | Mouse press event for focus or clear selection. |
| keyPressEvent | Key press event for ESC and up and down keys. |
| context_menu | Context menu. |
| insert_row | Insert row. |
| copy_row | Copy row. |
| remove_row | Remove row. |
| selection_changed | For Selection changed. |
| select_row | Select row. |
| closeEvent |  |
| set_row_height_hint |  |
| row_height_hint |  |
| clear_row_heights |  |
| setModel |  |


## <div class='my-heading' style='color: darkgreen;'>qt_event_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| gui_qt | Execute Qt GUI mode in IPython (if available). |
| _bundle_info | Info dictionary of the main bundle and helpers to call Objective-C (macOS only). |
| set_macos_app_name | Name of the application menu on macOS (instead of "Python"), set before the application is created. |
| macos_bundle_name | Name of the application menu on macOS. |
| get_qt_application | Get Qt application. |
| font_family | Font family available on this system. |
| font_style_sheet | Style sheet for application font. |
| busy_cursor | Show wait cursor during long operation. |
| with_busy_cursor | Decorator to show wait cursor while func is running. |
| error_summary | Short message of an exception: its type and the first line of its message. |
| send |  |
| sel |  |
| ns_string |  |
| py_string |  |
| wrapper |  |


### <div class='my-heading' style='color: royalblue;'>ExceptionHook

| Function | Summary |
|--------|----------|
| ExceptionHook | Exception hook. |
| _show_error | Show the error dialog for a full message. |
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


## <div class='my-heading' style='color: darkgreen;'>custom_widget.py

### <div class='my-heading' style='color: royalblue;'>Layout

| Function | Summary |
|--------|----------|
| Layout | Layout widget. |


### <div class='my-heading' style='color: royalblue;'>Panel

| Function | Summary |
|--------|----------|
| Panel | Panel widget. |


### <div class='my-heading' style='color: royalblue;'>Label

| Function | Summary |
|--------|----------|
| Label | Label widget. |
| set_background |  |
| sizeHint |  |


### <div class='my-heading' style='color: royalblue;'>MathWidget

| Function | Summary |
|--------|----------|
| MathWidget |  |
| setText |  |
| text |  |
| paintEvent |  |
| sizeHint |  |


### <div class='my-heading' style='color: royalblue;'>HBar

| Function | Summary |
|--------|----------|
| HBar | Horizontal bar widget. |


### <div class='my-heading' style='color: royalblue;'>VSpacer

| Function | Summary |
|--------|----------|
| VSpacer | Vertical spacer. |


### <div class='my-heading' style='color: royalblue;'>HSpacer

| Function | Summary |
|--------|----------|
| HSpacer | Horizontal spacer. |


### <div class='my-heading' style='color: royalblue;'>ColorSelector

| Function | Summary |
|--------|----------|
| ColorSelector | Color selector widget. |


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
| find_index | Find index (including match). |


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


### <div class='my-heading' style='color: royalblue;'>LineEdit

| Function | Summary |
|--------|----------|
| LineEdit |  |
| set_validator |  |
| setText |  |
| _validate |  |
| _update_style |  |
| raw_text |  |
| set_read_only |  |
| keyPressEvent |  |
| keyReleaseEvent |  |
| _set_edited |  |
| commit_pending | Apply text changed by user but not confirmed by Enter if valid, otherwise discard it. |
| focusOutEvent |  |
| focusInEvent |  |
| sizeHint |  |


### <div class='my-heading' style='color: royalblue;'>Editor

| Function | Summary |
|--------|----------|
| Editor | Editor widget with math/text display. |
| _on_return | Called when Enter is pressed in editor. |
| _on_focus_out | Handle focus-out safely. |
| clearFocus | Exit edit mode, safely restoring display. |
| mouseDoubleClickEvent | Switch to edit mode on double click. |
| mousePressEvent | Handle focus changes safely. |
| text | Return current text. |
| setText | Set editor and display text. |
| setCurrentText |  |
| sizeHint |  |


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
| showEvent |  |
| tab_change |  |
| _refresh_view_logic |  |


## <div class='my-heading' style='color: darkgreen;'>util_axis.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _create_label_axes_actor | Create label only orientation axes actor. |
| _create_axes_actor | Create custom axes actor. |
| _create_axes_actor_full | Create custom axes actor (crossed axes). |
| create_axes_widget | Create axes widget. |
| create_unit_cell | Create unit cell mesh. |
| create_cell_grid | Create grid point. |
| get_lattice_vector | Get lattice vector. |
| get_repeat_range | Get repeart range. |
| get_outside_box | Get indices outside range. |
| get_hkl_from_camera | Get index from camera. |
| get_camera_params | Get camera parameters. |


## <div class='my-heading' style='color: darkgreen;'>util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _check_shape | Check array shape. |
| str_to_sympy | Convert a string to a sympy. |
| to_latex | convert list to latex list. |
| _load_multipie | Import the parts of MultiPie used by QtDraw, which raises the error when they cannot be loaded. |
| check_multipie | Check if multipie is installed and can be loaded. |
| multipie_message | Tell why MultiPie cannot be used. |
| multipie_missing | Check if MultiPie is not installed, not only that it cannot be loaded. |
| install_multipie_command | Command to install MultiPie with pip of this Python. |
| command_text | Command as text to run in a shell, quoted. |
| create_grid | Create grid. |
| read_dict | Read dict text file. |
| to_plain | Convert numpy values in nested dict, list and tuple to Python values, which can be written as text and read again. |
| write_dict | write dict text file. |
| text_to_list | Convert single text to list. |
| apply | Apply function to (nested) list. |
| distance | group of sites with the same distance (in increasing order). |
| igrid | create integer grid points. |
| vec_latex |  |
| mat_latex |  |


### <div class='my-heading' style='color: royalblue;'>_NotFinite

| Function | Summary |
|--------|----------|
| visit_Name |  |


## <div class='my-heading' style='color: darkgreen;'>basic_object.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _str_poly_array | Convert from polynomial string to scalar array. |
| _str_vec_array | Convert from polynomial string (vector) to vector and scalar (abs.) arrays. |
| _svg_to_qimage |  |
| _create_image |  |
| _translate_and_orient | Translate and orient a mesh to a new center and direction. |
| create_sphere | Create sphere object. |
| create_bond | Create bond object. |
| arrow_length | Length of the arrow that create_vector() makes. |
| _arrow_tips | Arrow tips that can be made: a tip of length 0 or without direction is left out. |
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
| create_text2d | Create text 2d (math). |
| create_spline | Create spline object. |
| create_spline_t | Create parametric spline object. |
| create_isosurface | Create isosurface. |
| create_orbital_data | Create orbital object from data. |
| create_stream_data | Create steam vector object. |


## <div class='my-heading' style='color: darkgreen;'>read_material.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| parse_draw | Parse CIF, XSF, VESTA file without drawing. |
| draw | Draw parsed CIF, XSF, VESTA data. |
| read_draw | Read and draw CIF, XSF, VESTA file. |


## <div class='my-heading' style='color: darkgreen;'>util_parser.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| get_model_cell | Get model and cell. |
| get_site_info | Get site information. |
| get_bond_info | Get bond information. |
| draw_site_bond | Draw site and bond. |
| parse_material | Parse material file. |


## <div class='my-heading' style='color: darkgreen;'>converter.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| to_bool | Convert from string to bool. |
| get_status | Get update status. |
| get_camera | Get camera info. |
| get_preference | Get update preference. |
| get_multipie | Get multipie info. (v2->v3) |
| get_data | Get updated data. |
| convert_version3 | Converter from ver.1/2 to ver. 3. |


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
| cmd | Execute QtDraw. |


## <div class='my-heading' style='color: darkgreen;'>conv_qtdraw3.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| cmd | Convert QtDraw file of old version to version 3. |


## <div class='my-heading' style='color: darkgreen;'>cli_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| resolve_file | Resolve file name, ext is added if the file without it does not exist. |


## <div class='my-heading' style='color: darkgreen;'>tab_basis.py

### <div class='my-heading' style='color: royalblue;'>TabBasis

| Function | Summary |
|--------|----------|
| TabBasis |  |
| data | MultiPie data, read from the dialog each time (opening a file replaces it). |
| set_site |  |
| show_site_info |  |
| set_bond |  |
| show_bond_info |  |
| set_vector |  |
| show_vector_info |  |
| set_vector_list |  |
| set_orbital |  |
| show_orbital_info |  |
| set_orbital_list |  |
| show_bond_definition |  |
| show_site |  |
| show_bond |  |
| show_vector |  |
| show_vector_lc |  |
| show_orbital |  |
| show_orbital_lc |  |
| create_vector_modulation |  |
| create_orbital_modulation |  |
| show_vector_samb_modulation |  |
| show_orbital_samb_modulation |  |
| closeEvent |  |
| set_data |  |
| clear_data |  |


## <div class='my-heading' style='color: darkgreen;'>multipie_data.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _batched | Decorator: add objects in a batch, rendering once at its end (see PyVistaWidget._batch_render). |
| wrapper |  |


### <div class='my-heading' style='color: royalblue;'>MultiPieData

| Function | Summary |
|--------|----------|
| MultiPieData | MultiPie data manager. |
| group |  |
| ps_group |  |
| p_group |  |
| mp_group |  |
| _get_group_list |  |
| _get_group_name |  |
| _type_list |  |
| set_crystal_type |  |
| set_group_type |  |
| set_group |  |
| set_status |  |
| set_axis |  |
| clear_data |  |
| _set_counter |  |
| _get_index_list |  |
| set_group_find_wyckoff |  |
| add_site |  |
| add_bond |  |
| add_vector |  |
| add_orbital |  |
| add_bond_definition |  |
| site_samb_list |  |
| add_site_samb |  |
| bond_samb_list |  |
| add_bond_samb |  |
| vector_samb_list |  |
| add_vector_samb |  |
| add_vector_samb_modulation |  |
| orbital_samb_list |  |
| add_orbital_samb |  |
| add_orbital_samb_modulation |  |
| _parse_modulation | Parse modulation list. |
| _parse_range | Parse range. |


## <div class='my-heading' style='color: darkgreen;'>multipie_dialog.py

### <div class='my-heading' style='color: royalblue;'>MultiPieDialog

| Function | Summary |
|--------|----------|
| MultiPieDialog | MultiPie dialog. |
| _data | MultiPie data of the PyVistaWidget. |
| set_title |  |
| set_data | Show the MultiPie data. |
| clear_data |  |
| closeEvent |  |


## <div class='my-heading' style='color: darkgreen;'>multipie_modulation_dialog.py

### <div class='my-heading' style='color: royalblue;'>ModulationDialog

| Function | Summary |
|--------|----------|
| ModulationDialog |  |
| create_panel |  |
| set_view |  |
| modulation_range |  |
| create_modulation |  |
| add_data |  |
| remove_data |  |
| accept_data |  |
| reject_data |  |
| reset |  |


## <div class='my-heading' style='color: darkgreen;'>sub_group.py

### <div class='my-heading' style='color: royalblue;'>SubGroup

| Function | Summary |
|--------|----------|
| SubGroup |  |
| data | MultiPie data, read from the dialog each time (opening a file replaces it). |
| set_crystal_type |  |
| set_group_type |  |
| set_group |  |
| set_group_name |  |
| show_symmetry_operation |  |
| show_character_table |  |
| show_wyckoff_site |  |
| show_wyckoff_bond |  |
| show_product_table |  |
| closeEvent |  |
| set_data |  |
| clear_data |  |


## <div class='my-heading' style='color: darkgreen;'>tab_group.py

### <div class='my-heading' style='color: royalblue;'>TabGroup

| Function | Summary |
|--------|----------|
| TabGroup |  |
| data | MultiPie data, read from the dialog each time (opening a file replaces it). |
| set_irrep_list |  |
| set_harm_list |  |
| set_wyckoff_list |  |
| set_irrep_decomp |  |
| show_harmonics_decomp |  |
| show_harmonics |  |
| show_harmonics_info |  |
| show_wyckoff_site |  |
| show_wyckoff_bond |  |
| find_wyckoff_set |  |
| set_atomic_bra_ket |  |
| show_atomic |  |
| show_response |  |
| closeEvent |  |
| set_data |  |
| clear_data |  |


### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| _remove_latex |  |


## <div class='my-heading' style='color: darkgreen;'>multipie_util.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| phase_factor | Create phase factor. |
| create_samb_modulation |  |
| convert_vector_object |  |
| check_linear_combination |  |


## <div class='my-heading' style='color: darkgreen;'>tab_object.py

### <div class='my-heading' style='color: royalblue;'>TabObject

| Function | Summary |
|--------|----------|
| TabObject |  |
| data | MultiPie data, read from the dialog each time (opening a file replaces it). |
| show_site |  |
| show_bond |  |
| show_vector |  |
| show_orbital |  |
| closeEvent |  |
| set_data |  |
| clear_data |  |


## <div class='my-heading' style='color: darkgreen;'>multipie_info_dialog.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| show_group_info | Show group info. |
| show_symmetry_operation | Show symmetry operation panel. |
| show_character_table | Show character table panel. |
| show_wyckoff_site | Show Wyckoff position panel. |
| show_wyckoff_bond | Show Wyckoff position panel. |
| show_product_table | Show product table panel. |
| show_harmonics_decomp | Show harmonics decomposition panel. |
| show_harmonics_info | Show harmonics decomposition panel. |
| show_atomic_multipole | Show atomic multipole panel. |
| show_response | Show response tensor panel. |
| show_site_samb_panel | Show site SAMB panel. |
| show_bond_samb_panel | Show bond SAMB panel. |
| show_vector_samb_panel | Show vector SAMB panel. |
| show_orbital_samb_panel | Show orbital SAMB panel. |


### <div class='my-heading' style='color: royalblue;'>InfoPanel

| Function | Summary |
|--------|----------|
| InfoPanel | Info panel. |


## <div class='my-heading' style='color: darkgreen;'>multipie_plot.py

### <div class='my-heading' style='color: royalblue;'>Global function

| Function | Summary |
|--------|----------|
| plot_cell_site | Plot cell site. |
| plot_cell_bond | Plot cell bond. |
| plot_cell_vector | Plot cell vector. |
| plot_cell_multipole | Plot cell multipole. |
| plot_bond_definition |  |
| plot_site_cluster |  |
| plot_bond_cluster |  |
| plot_vector_cluster |  |
| plot_orbital_cluster |  |


