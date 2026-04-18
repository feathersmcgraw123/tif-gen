"""
Translation system for multi-language support.

Provides translations for English and Ukrainian.
"""

class Translator:
    """Simple translation system for UI text."""

    def __init__(self, language='en'):
        """
        Initialize translator.

        Args:
            language: Language code ('en' or 'uk')
        """
        self.language = language
        self.translations = {
            'en': ENGLISH,
            'uk': UKRAINIAN
        }

    def set_language(self, language):
        """Change the current language."""
        if language in self.translations:
            self.language = language
            return True
        return False

    def tr(self, key):
        """
        Get translated string.

        Args:
            key: Translation key

        Returns:
            Translated string, or key if not found
        """
        return self.translations.get(self.language, ENGLISH).get(key, key)

    def get_available_languages(self):
        """Get list of available languages."""
        return [
            ('en', 'English'),
            ('uk', 'Українська')
        ]


# English translations
ENGLISH = {
    # Main window
    'app_title': 'Satellite Imagery Export Tool',
    'menu_file': 'File',
    'menu_exit': 'Exit',
    'menu_help': 'Help',
    'menu_about': 'About',
    'menu_tile_sources': 'Tile Sources',
    'menu_language': 'Language',

    # Main window sections
    'section_polygon': '1. Define Export Polygon',
    'section_config': '2. Configure Export Settings',
    'section_export': '3. Start Export',
    'section_progress': 'Export Progress',

    # Polygon section
    'polygon_not_defined': 'No polygon defined',
    'polygon_defined': 'Polygon defined: {0} vertices',
    'btn_define_polygon': 'Define Polygon...',

    # Export button
    'btn_start_export': '3. Start Export',

    # Polygon dialog
    'dialog_polygon_title': 'Define Export Polygon',
    'tab_draw_map': '🗺️ Draw on Map',
    'tab_manual_entry': '✏️ Manual Entry',
    'tab_import_file': '📁 Import from File',
    'tab_preview': '👁️ Preview',

    # Map widget
    'map_instructions': 'Click on the map to add polygon vertices. Points will appear in order. Use the buttons below to manage points.',
    'btn_undo_point': 'Undo Last Point',
    'btn_clear_all': 'Clear All',
    'btn_reset_view': 'Reset View',
    'label_points': 'Points: {0}',

    # Manual entry
    'manual_instructions': 'Enter polygon vertices as latitude and longitude coordinates.\nPolygon will be automatically closed (first vertex repeated at end).',
    'header_latitude': 'Latitude',
    'header_longitude': 'Longitude',
    'btn_add_row': 'Add Row',
    'btn_remove_selected': 'Remove Selected',

    # Import from file
    'import_instructions': 'Import polygon coordinates from GeoJSON or CSV file.\nFor CSV files, specify which columns contain latitude and longitude.',
    'label_file': 'File:',
    'no_file_selected': 'No file selected',
    'btn_browse': 'Browse...',
    'label_lat_column': 'Latitude Column:',
    'label_lon_column': 'Longitude Column:',
    'label_file_preview': 'File Preview:',
    'btn_load_coords': 'Load Coordinates',

    # Preview tab
    'preview_instructions': 'Preview of defined polygon.\nShows polygon area and vertex count.',
    'preview_no_polygon': 'No polygon defined',
    'preview_stats': 'Vertices: {0} | Area: {1:.2f} km²',
    'label_polygon_coords': 'Polygon Coordinates:',
    'btn_refresh_preview': 'Refresh Preview',

    # Dialog buttons
    'btn_validate': 'Validate',
    'btn_ok': 'OK',
    'btn_cancel': 'Cancel',

    # Configuration widget
    'group_resolution': 'Resolution',
    'label_quality': 'Quality:',
    'quality_low': 'Low (Zoom 17, ~2.4 m/px)',
    'quality_medium': 'Medium (Zoom 18, ~1.2 m/px)',
    'quality_high': 'High (Zoom 19, ~0.6 m/px)',
    'advanced_mode': 'Advanced mode',
    'label_resolution': 'Resolution:',
    'label_zoom_level': 'Zoom Level:',
    'label_tile_size': 'Tile Size:',
    'group_compression': 'Compression',
    'label_compression_type': 'Type:',
    'label_jpeg_quality': 'JPEG Quality:',
    'group_output': 'Output',
    'label_crs': 'CRS:',
    'label_tile_source': 'Tile Source:',
    'label_output_file': 'Output File:',
    'group_advanced': 'Advanced',
    'label_render_delay': 'Render Delay:',
    'render_delay_tooltip': 'Delay between tile downloads.\nHigher values (0.3-0.5s) reduce rate limiting from tile servers.\nLower values speed up downloads but may cause failures.',
    'estimated_size': 'Estimated Size: {0}',
    'estimated_size_details': 'Estimated Size: {0} ({1}x{2} px, {3} tiles, zoom {4}, ≈{5:.2f} m/px)',
    'estimated_size_not_calculated': 'Estimated Size: Not calculated (no polygon defined)',
    'estimated_size_error': 'Estimated Size: Error calculating ({0})',

    # Progress widget
    'label_progress': 'Progress:',
    'label_current_tile': 'Current Tile:',
    'label_current_row': 'Current Row:',
    'label_elapsed': 'Elapsed:',
    'label_eta': 'ETA:',
    'label_status': 'Status:',
    'status_idle': 'Idle',
    'status_running': 'Running',
    'status_paused': 'Paused',
    'status_completed': 'Completed',
    'status_failed': 'Failed',
    'status_cancelled': 'Cancelled',
    'btn_pause': 'Pause',
    'btn_resume': 'Resume',
    'btn_cancel_export': 'Cancel',
    'label_log': 'Log:',

    # Messages
    'msg_no_coords': 'Please add at least 3 points to define a polygon.',
    'msg_invalid_polygon': 'Invalid Polygon',
    'msg_self_intersection': 'Self-Intersection',
    'msg_validation_success': 'Validation Success',
    'msg_polygon_valid': 'Polygon is valid!\n\nVertices: {0}\nArea: {1:.2f} km²',
    'msg_error': 'Error',
    'msg_success': 'Success',
    'msg_loaded_vertices': 'Loaded {0} vertices from file',

    # Export messages
    'msg_invalid_config': 'Invalid Configuration',
    'msg_no_polygon': 'No Polygon',
    'msg_define_polygon_first': 'Please define an export polygon first.',
    'msg_output_path_error': 'Output Path Error',
    'msg_insufficient_disk_space': 'Insufficient Disk Space',
    'msg_disk_space_warning': 'Estimated output size: {0}\nAvailable disk space: {1}\n\nPlease free up disk space or choose a different output location.',
    'msg_start_export': 'Start Export',
    'msg_start_export_confirm': 'Ready to start export.\n\nOutput: {0}\nEstimated size: {1}\n\nThis may take several minutes to hours depending on the area size.\nContinue?',
    'msg_export_complete': 'Export Complete',
    'msg_export_complete_text': 'Export completed successfully!\n\n{0}',
    'msg_export_failed': 'Export Failed',
    'msg_export_failed_text': 'Export failed:\n\n{0}',
    'msg_cancel_export': 'Cancel Export',
    'msg_cancel_export_confirm': 'Are you sure you want to cancel the export?\n\nProgress will be lost and partial files will be deleted.',
    'msg_export_in_progress': 'Export in Progress',
    'msg_export_in_progress_quit': 'An export is currently running. Are you sure you want to quit?\n\nThe export will be cancelled and progress will be lost.',

    # About dialog
    'about_title': 'About Satellite Imagery Export Tool',
    'about_text': '<h3>Satellite Imagery Export Tool</h3>'
                  '<p>Version 2.0 - Standalone Edition</p>'
                  '<p>Export high-resolution georeferenced GeoTIFF files from online tile sources.</p>'
                  '<p><b>Features:</b></p>'
                  '<ul>'
                  '<li>Interactive map for polygon definition</li>'
                  '<li>Direct tile downloading from multiple sources (Google, ESRI, Bing, OSM, etc.)</li>'
                  '<li>Define export polygons manually or from files (GeoJSON, CSV)</li>'
                  '<li>Configurable resolution and compression</li>'
                  '<li>Automatic zoom level calculation</li>'
                  '<li>Pause/resume/cancel support</li>'
                  '<li>No QGIS installation required</li>'
                  '</ul>'
                  '<p>Built with rasterio, PyQt5, and Python.</p>',

    # Tile sources dialog
    'tile_sources_title': 'Tile Sources',
    'tile_sources_note': '<p><b>Note:</b> Usage of these tile sources is subject to their respective terms of service.</p>',

    # File dialogs
    'select_polygon_file': 'Select Polygon File',
    'select_output_file': 'Select Output File',
    'geotiff_files': 'GeoTIFF Files (*.tif *.tiff);;All Files (*)',
    'geojson_files': 'GeoJSON Files (*.geojson *.json);;CSV Files (*.csv);;All Files (*)',

    # Validation errors
    'error_empty_cell': 'Empty cell at row {0}',
    'error_invalid_number': 'Invalid number at row {0}',
    'error_output_path_required': 'Output file path is required',
    'error_no_tile_source': 'No tile source selected',
}


# Ukrainian translations
UKRAINIAN = {
    # Main window
    'app_title': 'Інструмент експорту супутникових зображень',
    'menu_file': 'Файл',
    'menu_exit': 'Вихід',
    'menu_help': 'Довідка',
    'menu_about': 'Про програму',
    'menu_tile_sources': 'Джерела тайлів',
    'menu_language': 'Мова',

    # Main window sections
    'section_polygon': '1. Визначити полігон експорту',
    'section_config': '2. Налаштувати параметри експорту',
    'section_export': '3. Розпочати експорт',
    'section_progress': 'Прогрес експорту',

    # Polygon section
    'polygon_not_defined': 'Полігон не визначено',
    'polygon_defined': 'Полігон визначено: {0} вершин',
    'btn_define_polygon': 'Визначити полігон...',

    # Export button
    'btn_start_export': '3. Розпочати експорт',

    # Polygon dialog
    'dialog_polygon_title': 'Визначити полігон експорту',
    'tab_draw_map': '🗺️ Малювати на карті',
    'tab_manual_entry': '✏️ Ручне введення',
    'tab_import_file': '📁 Імпорт з файлу',
    'tab_preview': '👁️ Попередній перегляд',

    # Map widget
    'map_instructions': 'Клацніть на карті, щоб додати вершини полігона. Точки з\'являтимуться по порядку. Використовуйте кнопки нижче для керування точками.',
    'btn_undo_point': 'Скасувати останню точку',
    'btn_clear_all': 'Очистити все',
    'btn_reset_view': 'Скинути вигляд',
    'label_points': 'Точок: {0}',

    # Manual entry
    'manual_instructions': 'Введіть вершини полігона як координати широти та довготи.\nПолігон буде автоматично замкнено (перша вершина повториться в кінці).',
    'header_latitude': 'Широта',
    'header_longitude': 'Довгота',
    'btn_add_row': 'Додати рядок',
    'btn_remove_selected': 'Видалити вибране',

    # Import from file
    'import_instructions': 'Імпортувати координати полігона з файлу GeoJSON або CSV.\nДля файлів CSV вкажіть, які стовпці містять широту та довготу.',
    'label_file': 'Файл:',
    'no_file_selected': 'Файл не вибрано',
    'btn_browse': 'Огляд...',
    'label_lat_column': 'Стовпець широти:',
    'label_lon_column': 'Стовпець довготи:',
    'label_file_preview': 'Попередній перегляд файлу:',
    'btn_load_coords': 'Завантажити координати',

    # Preview tab
    'preview_instructions': 'Попередній перегляд визначеного полігона.\nПоказує площу полігона та кількість вершин.',
    'preview_no_polygon': 'Полігон не визначено',
    'preview_stats': 'Вершин: {0} | Площа: {1:.2f} км²',
    'label_polygon_coords': 'Координати полігона:',
    'btn_refresh_preview': 'Оновити попередній перегляд',

    # Dialog buttons
    'btn_validate': 'Перевірити',
    'btn_ok': 'ОК',
    'btn_cancel': 'Скасувати',

    # Configuration widget
    'group_resolution': 'Роздільна здатність',
    'label_quality': 'Якість:',
    'quality_low': 'Низька (Зум 17, ~2.4 м/пікс)',
    'quality_medium': 'Середня (Зум 18, ~1.2 м/пікс)',
    'quality_high': 'Висока (Зум 19, ~0.6 м/пікс)',
    'advanced_mode': 'Розширений режим',
    'label_resolution': 'Роздільна здатність:',
    'label_zoom_level': 'Рівень масштабування:',
    'label_tile_size': 'Розмір тайлу:',
    'group_compression': 'Стиснення',
    'label_compression_type': 'Тип:',
    'label_jpeg_quality': 'Якість JPEG:',
    'group_output': 'Вихідні дані',
    'label_crs': 'CRS:',
    'label_tile_source': 'Джерело тайлів:',
    'label_output_file': 'Вихідний файл:',
    'group_advanced': 'Розширені',
    'label_render_delay': 'Затримка рендерингу:',
    'render_delay_tooltip': 'Затримка між завантаженнями тайлів.\nВищі значення (0.3-0.5с) зменшують обмеження швидкості від серверів тайлів.\nНижчі значення прискорюють завантаження, але можуть спричинити помилки.',
    'estimated_size': 'Очікуваний розмір: {0}',
    'estimated_size_details': 'Очікуваний розмір: {0} ({1}x{2} пікс, {3} тайлів, зум {4}, ≈{5:.2f} м/пікс)',
    'estimated_size_not_calculated': 'Очікуваний розмір: Не обчислено (полігон не визначено)',
    'estimated_size_error': 'Очікуваний розмір: Помилка обчислення ({0})',

    # Progress widget
    'label_progress': 'Прогрес:',
    'label_current_tile': 'Поточний тайл:',
    'label_current_row': 'Поточний рядок:',
    'label_elapsed': 'Минуло:',
    'label_eta': 'Залишилось:',
    'label_status': 'Статус:',
    'status_idle': 'Очікування',
    'status_running': 'Виконується',
    'status_paused': 'Призупинено',
    'status_completed': 'Завершено',
    'status_failed': 'Помилка',
    'status_cancelled': 'Скасовано',
    'btn_pause': 'Призупинити',
    'btn_resume': 'Продовжити',
    'btn_cancel_export': 'Скасувати',
    'label_log': 'Журнал:',

    # Messages
    'msg_no_coords': 'Будь ласка, додайте принаймні 3 точки для визначення полігона.',
    'msg_invalid_polygon': 'Недійсний полігон',
    'msg_self_intersection': 'Самоперетин',
    'msg_validation_success': 'Перевірка успішна',
    'msg_polygon_valid': 'Полігон дійсний!\n\nВершин: {0}\nПлоща: {1:.2f} км²',
    'msg_error': 'Помилка',
    'msg_success': 'Успіх',
    'msg_loaded_vertices': 'Завантажено {0} вершин з файлу',

    # Export messages
    'msg_invalid_config': 'Недійсна конфігурація',
    'msg_no_polygon': 'Немає полігона',
    'msg_define_polygon_first': 'Спочатку визначте полігон експорту.',
    'msg_output_path_error': 'Помилка вихідного шляху',
    'msg_insufficient_disk_space': 'Недостатньо місця на диску',
    'msg_disk_space_warning': 'Очікуваний розмір виводу: {0}\nДоступно місця на диску: {1}\n\nБудь ласка, звільніть місце на диску або виберіть інше місце виводу.',
    'msg_start_export': 'Розпочати експорт',
    'msg_start_export_confirm': 'Готово розпочати експорт.\n\nВихід: {0}\nОчікуваний розмір: {1}\n\nЦе може зайняти від кількох хвилин до годин залежно від розміру області.\nПродовжити?',
    'msg_export_complete': 'Експорт завершено',
    'msg_export_complete_text': 'Експорт успішно завершено!\n\n{0}',
    'msg_export_failed': 'Експорт не вдався',
    'msg_export_failed_text': 'Експорт не вдався:\n\n{0}',
    'msg_cancel_export': 'Скасувати експорт',
    'msg_cancel_export_confirm': 'Ви впевнені, що хочете скасувати експорт?\n\nПрогрес буде втрачено, а часткові файли будуть видалені.',
    'msg_export_in_progress': 'Експорт виконується',
    'msg_export_in_progress_quit': 'Експорт зараз виконується. Ви впевнені, що хочете вийти?\n\nЕкспорт буде скасовано, а прогрес буде втрачено.',

    # About dialog
    'about_title': 'Про інструмент експорту супутникових зображень',
    'about_text': '<h3>Інструмент експорту супутникових зображень</h3>'
                  '<p>Версія 2.0 - Автономне видання</p>'
                  '<p>Експорт високороздільних геоприв\'язаних файлів GeoTIFF з онлайн-джерел тайлів.</p>'
                  '<p><b>Функції:</b></p>'
                  '<ul>'
                  '<li>Інтерактивна карта для визначення полігона</li>'
                  '<li>Пряме завантаження тайлів з кількох джерел (Google, ESRI, Bing, OSM тощо)</li>'
                  '<li>Визначення полігонів експорту вручну або з файлів (GeoJSON, CSV)</li>'
                  '<li>Налаштовувана роздільна здатність та стиснення</li>'
                  '<li>Автоматичний розрахунок рівня масштабування</li>'
                  '<li>Підтримка призупинення/відновлення/скасування</li>'
                  '<li>Не потребує встановлення QGIS</li>'
                  '</ul>'
                  '<p>Створено з rasterio, PyQt5 та Python.</p>',

    # Tile sources dialog
    'tile_sources_title': 'Джерела тайлів',
    'tile_sources_note': '<p><b>Примітка:</b> Використання цих джерел тайлів підлягає їх відповідним умовам обслуговування.</p>',

    # File dialogs
    'select_polygon_file': 'Вибрати файл полігона',
    'select_output_file': 'Вибрати вихідний файл',
    'geotiff_files': 'Файли GeoTIFF (*.tif *.tiff);;Усі файли (*)',
    'geojson_files': 'Файли GeoJSON (*.geojson *.json);;Файли CSV (*.csv);;Усі файли (*)',

    # Validation errors
    'error_empty_cell': 'Порожня комірка в рядку {0}',
    'error_invalid_number': 'Недійсне число в рядку {0}',
    'error_output_path_required': 'Вихідний шлях файлу обов\'язковий',
    'error_no_tile_source': 'Джерело тайлів не вибрано',
}


# Global translator instance
_translator = Translator('en')


def get_translator():
    """Get global translator instance."""
    return _translator


def tr(key):
    """Shorthand for translation."""
    return _translator.tr(key)
