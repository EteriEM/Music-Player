import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QHBoxLayout, QSlider, QComboBox, QTreeWidget, QTreeWidgetItem, QLineEdit, QMessageBox
import webbrowser
from PyQt5.QtCore import Qt, QTimer
import vlc
import os
from PyQt5.QtGui import QPixmap, QIcon
from mutagen import File as MutagenFile
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
from mutagen.flac import Picture
from PIL import Image, ImageQt
from io import BytesIO

# Replace with your actual VLC install path
os.add_dll_directory(r"D:\VLC")

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Music Player')
        self.setGeometry(100, 100, 520, 600)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(16)

        # Main content layout (album art and controls side by side)
        main_layout = QHBoxLayout()
        
        # Left side - Sorting and playlist
        left_layout = QVBoxLayout()
        
        # Sorting mode dropdown
        self.sort_mode = QComboBox()
        self.sort_mode.addItems(['All Songs', 'By Artist & Album', 'By Album', 'By Artist'])
        self.sort_mode.currentIndexChanged.connect(self.update_playlist_view)
        self.sort_mode.setStyleSheet('QComboBox { background-color: white; color: #333; border: 1px solid #ccc; padding: 4px 8px; font-size: 13px; } QComboBox QAbstractItemView { background-color: white; color: #333; }')
        left_layout.addWidget(self.sort_mode)
        
        # Playlist (QTreeWidget for grouping)
        self.playlist = []
        self.metadata_list = []  # Store metadata for sorting
        self.current_index = -1
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemClicked.connect(self.select_track)
        self.tree_widget.setStyleSheet('QTreeWidget { background-color: white; color: #333; border: 1px solid #ddd; font-size: 13px; } QTreeWidget::item { padding: 4px 8px; } QTreeWidget::item:selected { background: #e3f2fd; color: #333; }')
        left_layout.addWidget(self.tree_widget)
        
        main_layout.addLayout(left_layout, 1)  # 1 = stretch factor
        
        # Right side - Player controls
        right_layout = QVBoxLayout()
        
        # Album art
        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(180, 180)
        self.album_art_label.setStyleSheet('background-color: #f0f0f0; border: 1px solid #ddd;')
        self.album_art_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(self.album_art_label, alignment=Qt.AlignCenter)

        # Song metadata
        self.title_label = QLabel('Title: -')
        self.title_label.setStyleSheet('color: #333; font-size: 18px; font-weight: bold; margin-top: 8px;')
        self.artist_label = QLabel('Artist: -')
        self.artist_label.setStyleSheet('color: #666; font-size: 14px; margin-top: 2px;')
        self.album_label = QLabel('Album: -')
        self.album_label.setStyleSheet('color: #666; font-size: 14px; margin-bottom: 8px;')
        for l in [self.title_label, self.artist_label, self.album_label]:
            right_layout.addWidget(l, alignment=Qt.AlignCenter)

        self.label = QLabel('No file selected')
        self.label.setStyleSheet('color: #888; font-size: 12px; margin-bottom: 8px;')
        right_layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # Streaming controls
        stream_layout = QHBoxLayout()
        
        self.stream_url_input = QLineEdit()
        self.stream_url_input.setPlaceholderText('Enter stream URL')
        self.stream_url_input.setStyleSheet('QLineEdit { background-color: white; color: #333; border: 1px solid #ccc; padding: 6px 8px; font-size: 12px; }')
        stream_layout.addWidget(self.stream_url_input)
        
        self.connect_button = QPushButton('Connect')
        self.connect_button.setStyleSheet('QPushButton { background-color: #4a90e2; color: white; border: none; padding: 6px 12px; font-size: 12px; } QPushButton:hover { background-color: #357abd; }')
        self.connect_button.clicked.connect(self.connect_to_stream)
        stream_layout.addWidget(self.connect_button)
        
        right_layout.addLayout(stream_layout)
        
        # Local file button (optional)
        self.open_button = QPushButton('Open Local Files')
        self.open_button.setStyleSheet('QPushButton { background-color: #6c757d; color: white; border: none; padding: 6px 12px; font-size: 12px; margin-top: 8px; } QPushButton:hover { background-color: #5a6268; }')
        self.open_button.clicked.connect(self.open_files)
        right_layout.addWidget(self.open_button, alignment=Qt.AlignCenter)
        
        # GitHub integration buttons
        github_layout = QHBoxLayout()
        
        self.github_button = QPushButton('📚 GitHub')
        self.github_button.setStyleSheet('QPushButton { background-color: #24292e; color: white; border: none; padding: 6px 12px; font-size: 12px; } QPushButton:hover { background-color: #2f363d; }')
        self.github_button.clicked.connect(self.open_github)
        github_layout.addWidget(self.github_button)
        
        self.issues_button = QPushButton('🐛 Report Issue')
        self.issues_button.setStyleSheet('QPushButton { background-color: #d73a49; color: white; border: none; padding: 6px 12px; font-size: 12px; } QPushButton:hover { background-color: #cb2431; }')
        self.issues_button.clicked.connect(self.report_issue)
        github_layout.addWidget(self.issues_button)
        
        right_layout.addLayout(github_layout)
        
        main_layout.addLayout(right_layout, 1)  # 1 = stretch factor
        
        self.layout.addLayout(main_layout)

        # Controls layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(24)
        controls_layout.setContentsMargins(0, 12, 0, 12)

        btn_style = 'QPushButton { background: #f8f9fa; color: #333; border: 1px solid #ddd; font-size: 18px; min-width: 40px; min-height: 40px; } QPushButton:hover { background: #e9ecef; }'

        self.backward_button = QPushButton()
        self.backward_button.setIcon(QIcon.fromTheme('media-skip-backward'))
        self.backward_button.setText('⏮')
        self.backward_button.setStyleSheet(btn_style)
        self.backward_button.clicked.connect(self.backward)
        self.backward_button.setEnabled(False)
        controls_layout.addWidget(self.backward_button)

        self.play_button = QPushButton()
        self.play_button.setIcon(QIcon.fromTheme('media-playback-start'))
        self.play_button.setText('▶')
        self.play_button.setStyleSheet(btn_style)
        self.play_button.clicked.connect(self.play_music)
        self.play_button.setEnabled(False)
        controls_layout.addWidget(self.play_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(QIcon.fromTheme('media-playback-stop'))
        self.stop_button.setText('⏹')
        self.stop_button.setStyleSheet(btn_style)
        self.stop_button.clicked.connect(self.stop_music)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon.fromTheme('media-skip-forward'))
        self.forward_button.setText('⏭')
        self.forward_button.setStyleSheet(btn_style)
        self.forward_button.clicked.connect(self.forward)
        self.forward_button.setEnabled(False)
        controls_layout.addWidget(self.forward_button)

        self.layout.addLayout(controls_layout)

        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        self.progress_slider.setStyleSheet('QSlider::groove:horizontal { height: 6px; background: #e9ecef; border-radius: 3px; } QSlider::handle:horizontal { background: #4a90e2; border: 1px solid #ccc; width: 16px; margin: -5px 0; border-radius: 8px; } QSlider::sub-page:horizontal { background: #4a90e2; border-radius: 3px; }')
        self.layout.addWidget(self.progress_slider)

        # Time display
        time_layout = QHBoxLayout()
        self.elapsed_label = QLabel('0:00')
        self.elapsed_label.setStyleSheet('color: #666; font-size: 12px;')
        self.remaining_label = QLabel('-0:00')
        self.remaining_label.setStyleSheet('color: #666; font-size: 12px;')
        time_layout.addWidget(self.elapsed_label)
        time_layout.addStretch()
        time_layout.addWidget(self.remaining_label)
        self.layout.addLayout(time_layout)

        # Volume slider
        volume_layout = QHBoxLayout()
        self.volume_label = QLabel('Volume:')
        self.volume_label.setStyleSheet('color: #666; font-size: 12px;')
        volume_layout.addWidget(self.volume_label)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.setStyleSheet('QSlider::groove:horizontal { height: 6px; background: #e9ecef; border-radius: 3px; } QSlider::handle:horizontal { background: #4a90e2; border: 1px solid #ccc; width: 12px; margin: -3px 0; border-radius: 6px; } QSlider::sub-page:horizontal { background: #4a90e2; border-radius: 3px; }')
        volume_layout.addWidget(self.volume_slider)
        self.layout.addLayout(volume_layout)

        # Timer for updating progress
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_progress)

        self.setLayout(self.layout)
        self.media_player = None
        self.is_streaming = False
        self.stream_url = None
        self.setStyleSheet('background-color: #fafafa;')

    def connect_to_stream(self):
        url = self.stream_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Error', 'Please enter a stream URL')
            return
        
        try:
            # Test the URL by creating a media object
            media = vlc.Media(url)
            if media:
                self.stream_url = url
                self.is_streaming = True
                self.playlist = [url]
                self.metadata_list = [{'title': 'Streaming Audio', 'artist': 'Live Stream', 'album': 'Network Stream', 'tracknumber': '1'}]
                self.current_index = 0
                self.label.setText(f'Connected to: {url}')
                self.update_playlist_view()
                self.play_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.forward_button.setEnabled(False)  # No forward/backward for streams
                self.backward_button.setEnabled(False)
                self.progress_slider.setValue(0)
                self.update_metadata_and_art()
                QMessageBox.information(self, 'Success', f'Connected to stream: {url}')
            else:
                QMessageBox.warning(self, 'Error', 'Could not connect to the stream URL')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to connect to stream: {str(e)}')

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Open Music Files', '', 'Audio Files (*.mp3 *.flac *.wav *.ogg *.m4a)')
        if files:
            self.is_streaming = False
            self.stream_url = None
            self.playlist = files
            self.metadata_list = [self.extract_metadata(f) for f in files]
            self.current_index = 0
            self.label.setText(self.playlist[self.current_index])
            self.update_playlist_view()
            self.play_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.forward_button.setEnabled(len(self.playlist) > 1)
            self.backward_button.setEnabled(len(self.playlist) > 1)
            self.progress_slider.setValue(0)
            self.update_metadata_and_art()

    def update_playlist_view(self):
        mode = self.sort_mode.currentText()
        self.tree_widget.clear()
        self.tree_widget.setColumnCount(1)
        
        # Prepare data for grouping
        items = []
        for i, meta in enumerate(self.metadata_list):
            item = dict(meta)
            item['index'] = i
            items.append(item)
        
        # Helper: sort by track number then title
        def sort_key(x):
            try:
                track = int(x.get('tracknumber', '0').split('/')[0])
            except Exception:
                track = 0
            return (x.get('album', ''), track, x.get('title', ''))
        
        if mode == 'All Songs':
            # Show as flat list with file icons
            for item in sorted(items, key=sort_key):
                node = QTreeWidgetItem([f"📄 {item['title']}"])
                node.setData(0, Qt.UserRole, item['index'])
                self.tree_widget.addTopLevelItem(node)
                
        elif mode == 'By Artist & Album':
            # File system structure: Artist/Album/Song
            artists = {}
            for item in items:
                artist = item['artist']
                album = item['album']
                if artist not in artists:
                    artists[artist] = {}
                if album not in artists[artist]:
                    artists[artist][album] = []
                artists[artist][album].append(item)
            
            for artist in sorted(artists):
                artist_node = QTreeWidgetItem([f"📁 {artist}"])
                artist_node.setFlags(artist_node.flags() & ~Qt.ItemIsSelectable)
                self.tree_widget.addTopLevelItem(artist_node)
                
                for album in sorted(artists[artist]):
                    album_node = QTreeWidgetItem([f"📁 {album}"])
                    album_node.setFlags(album_node.flags() & ~Qt.ItemIsSelectable)
                    artist_node.addChild(album_node)
                    
                    for song in sorted(artists[artist][album], key=sort_key):
                        song_node = QTreeWidgetItem([f"🎵 {song['title']}"])
                        song_node.setData(0, Qt.UserRole, song['index'])
                        album_node.addChild(song_node)
                        
        elif mode == 'By Album':
            # File system structure: Album/Song
            albums = {}
            for item in items:
                album = item['album']
                if album not in albums:
                    albums[album] = []
                albums[album].append(item)
            
            for album in sorted(albums):
                album_node = QTreeWidgetItem([f"📁 {album}"])
                album_node.setFlags(album_node.flags() & ~Qt.ItemIsSelectable)
                self.tree_widget.addTopLevelItem(album_node)
                
                for song in sorted(albums[album], key=sort_key):
                    song_node = QTreeWidgetItem([f"🎵 {song['title']} - {song['artist']}"])
                    song_node.setData(0, Qt.UserRole, song['index'])
                    album_node.addChild(song_node)
                    
        elif mode == 'By Artist':
            # File system structure: Artist/Song
            artists = {}
            for item in items:
                artist = item['artist']
                if artist not in artists:
                    artists[artist] = []
                artists[artist].append(item)
            
            for artist in sorted(artists):
                artist_node = QTreeWidgetItem([f"📁 {artist}"])
                artist_node.setFlags(artist_node.flags() & ~Qt.ItemIsSelectable)
                self.tree_widget.addTopLevelItem(artist_node)
                
                for song in sorted(artists[artist], key=sort_key):
                    song_node = QTreeWidgetItem([f"🎵 {song['title']} - {song['album']}"])
                    song_node.setData(0, Qt.UserRole, song['index'])
                    artist_node.addChild(song_node)
        
        self.tree_widget.expandAll()
        # Highlight current song
        self.highlight_current_song()

    def select_track(self, item, column):
        index = item.data(0, Qt.UserRole)
        if index is not None:
            self.current_index = index
            self.label.setText(self.playlist[self.current_index])
            self.play_music()
            self.progress_slider.setValue(0)
            self.update_metadata_and_art()

    def play_music(self):
        if self.playlist and self.current_index != -1:
            if self.media_player:
                self.media_player.stop()
            self.media_player = vlc.MediaPlayer(self.playlist[self.current_index])
            self.media_player.play()
            self.set_volume()  # Set initial volume
            self.stop_button.setEnabled(True)
            self.timer.start()
            self.update_metadata_and_art()

    def stop_music(self):
        if self.media_player:
            self.media_player.stop()
            self.stop_button.setEnabled(False)
            self.timer.stop()
            self.progress_slider.setValue(0)

    def update_progress(self):
        if self.media_player:
            try:
                if self.is_streaming:
                    # For streams, just show elapsed time
                    pos = self.media_player.get_time()
                    if pos >= 0:
                        self.elapsed_label.setText(self.format_time(pos))
                        self.remaining_label.setText('--:--')  # Unknown duration for streams
                else:
                    # For local files, show progress and remaining time
                    length = self.media_player.get_length()
                    pos = self.media_player.get_time()
                    if length > 0:
                        value = int((pos / length) * 1000)
                        self.progress_slider.blockSignals(True)
                        self.progress_slider.setValue(value)
                        self.progress_slider.blockSignals(False)
                        # Update time labels
                        self.elapsed_label.setText(self.format_time(pos))
                        self.remaining_label.setText('-' + self.format_time(length - pos))
            except Exception:
                pass

    def seek_position(self, value):
        if self.media_player and not self.is_streaming:
            # Only allow seeking for local files, not streams
            length = self.media_player.get_length()
            if length > 0:
                new_time = int((value / 1000) * length)
                self.media_player.set_time(new_time)

    def set_volume(self):
        if self.media_player:
            self.media_player.audio_set_volume(self.volume_slider.value())

    def forward(self):
        if self.playlist and self.current_index < len(self.playlist) - 1 and not self.is_streaming:
            self.current_index += 1
            self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(self.current_index))
            self.label.setText(self.playlist[self.current_index])
            self.play_music()
            self.progress_slider.setValue(0)
            self.update_metadata_and_art()

    def backward(self):
        if self.playlist and self.current_index > 0 and not self.is_streaming:
            self.current_index -= 1
            self.tree_widget.setCurrentItem(self.tree_widget.topLevelItem(self.current_index))
            self.label.setText(self.playlist[self.current_index])
            self.play_music()
            self.progress_slider.setValue(0)
            self.update_metadata_and_art()

    def get_display_name(self, filepath):
        # Try to get title from metadata, else filename
        try:
            audio = MutagenFile(filepath, easy=True)
            if audio and 'title' in audio:
                return audio['title'][0]
        except Exception:
            pass
        return os.path.basename(filepath)

    def extract_metadata(self, filepath):
        # Returns a dict with title, artist, album, tracknumber
        title, artist, album, tracknumber = '-', '-', '-', '0'
        try:
            audio = MutagenFile(filepath, easy=True)
            if audio:
                title = audio.get('title', [os.path.basename(filepath)])[0]
                artist = audio.get('artist', ['-'])[0]
                album = audio.get('album', ['-'])[0]
                tracknumber = audio.get('tracknumber', ['0'])[0]
        except Exception:
            pass
        return {'title': title, 'artist': artist, 'album': album, 'tracknumber': tracknumber}

    def update_metadata_and_art(self):
        if not self.playlist or self.current_index == -1:
            self.title_label.setText('Title: -')
            self.artist_label.setText('Artist: -')
            self.album_label.setText('Album: -')
            self.album_art_label.clear()
            return
        
        if self.is_streaming:
            # For streams, use the metadata we set
            metadata = self.metadata_list[self.current_index]
            self.title_label.setText(f'Title: {metadata["title"]}')
            self.artist_label.setText(f'Artist: {metadata["artist"]}')
            self.album_label.setText(f'Album: {metadata["album"]}')
            self.album_art_label.clear()
            return
            
        filepath = self.playlist[self.current_index]
        title, artist, album = '-', '-', '-'
        art = None
        try:
            audio = MutagenFile(filepath)
            if audio is not None:
                if audio.tags:
                    if 'TIT2' in audio.tags:
                        title = str(audio.tags['TIT2'])
                    if 'TPE1' in audio.tags:
                        artist = str(audio.tags['TPE1'])
                    if 'TALB' in audio.tags:
                        album = str(audio.tags['TALB'])
                # FLAC
                if hasattr(audio, 'pictures') and audio.pictures:
                    art = audio.pictures[0].data
                # MP3
                elif 'APIC:' in audio.tags:
                    art = audio.tags['APIC:'].data
        except Exception:
            pass
        self.title_label.setText(f'Title: {title}')
        self.artist_label.setText(f'Artist: {artist}')
        self.album_label.setText(f'Album: {album}')
        if art:
            image = Image.open(BytesIO(art))
            image = image.resize((200, 200))
            qt_image = QPixmap.fromImage(ImageQt(image))
            self.album_art_label.setPixmap(qt_image)
        else:
            self.album_art_label.clear()

    def format_time(self, ms):
        seconds = int(ms / 1000)
        m, s = divmod(seconds, 60)
        return f'{m}:{s:02d}'

    def highlight_current_song(self):
        # Recursively search for the item with current_index and select it
        def search_items(parent):
            for i in range(parent.childCount()):
                child = parent.child(i)
                idx = child.data(0, Qt.UserRole)
                if idx == self.current_index:
                    self.tree_widget.setCurrentItem(child)
                    return True
                if search_items(child):
                    return True
            return False
        # Top-level
        for i in range(self.tree_widget.topLevelItemCount()):
            item = self.tree_widget.topLevelItem(i)
            idx = item.data(0, Qt.UserRole)
            if idx == self.current_index:
                self.tree_widget.setCurrentItem(item)
                return
            if search_items(item):
                return

    def open_github(self):
        """Open the GitHub repository in the default browser"""
        github_url = "https://github.com/yourusername/music-player"
        try:
            webbrowser.open(github_url)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open GitHub: {str(e)}')

    def report_issue(self):
        """Open GitHub issues page in the default browser"""
        issues_url = "https://github.com/yourusername/music-player/issues/new"
        try:
            webbrowser.open(issues_url)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not open issues page: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_()) 