# Music Player

A modern, feature-rich music player built with Python and PyQt5, supporting both local files and network streaming.

## Features

- 🎵 **Local File Playback**: Support for MP3, FLAC, WAV, OGG, M4A
- 🌐 **Network Streaming**: Stream audio from HTTP URLs
- 📁 **File System View**: Browse music like a file explorer with folder icons
- 🎨 **Album Art Display**: Shows embedded album artwork
- 📊 **Metadata Support**: Displays title, artist, album information
- 🎚️ **Volume Control**: Adjustable volume slider
- ⏯️ **Playback Controls**: Play, stop, forward, backward
- 📈 **Progress Tracking**: Seek through tracks with progress bar
- 🗂️ **Multiple Sort Views**: 
  - All Songs (flat list)
  - By Artist & Album (hierarchical)
  - By Album
  - By Artist
- 🎯 **Track Selection**: Click any song to play instantly

## Screenshots

The player features a clean, modern interface with:
- Left panel: File system-style playlist browser
- Right panel: Player controls and album artwork
- Streaming support for network audio sources

## Requirements

- Python 3.7+
- PyQt5
- python-vlc
- mutagen
- Pillow (PIL)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/music-player.git
cd music-player
```

2. Install dependencies:
```bash
pip install PyQt5 python-vlc mutagen Pillow
```

3. Install VLC media player:
   - Download from [VLC website](https://www.videolan.org/vlc/)
   - Update the VLC path in `music_player.py` line 15:
   ```python
   os.add_dll_directory(r"path/to/your/vlc/installation")
   ```

## Usage

### Local Files
1. Click "Open Local Files"
2. Select your music files
3. Browse and play using the file system interface

### Network Streaming
1. Enter the stream URL (e.g., `http://192.168.1.100:8000/stream.mp3`)
2. Click "Connect"
3. Use play/stop controls to manage the stream

### Navigation
- Use the sorting dropdown to change the playlist view
- Click on folders to expand/collapse
- Click on songs to play them
- Use the progress slider to seek (local files only)

## Supported Stream Formats

- HTTP streams
- Icecast streams
- Local network streams
- Any format supported by VLC

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- Audio playback powered by [VLC](https://www.videolan.org/)
- Metadata handling with [mutagen](https://mutagen.readthedocs.io/)

## Issues

If you encounter any issues, please [open an issue](https://github.com/yourusername/music-player/issues) on GitHub.
