wikipedia_music_tagger
======================

Feed date_tagger.py a list of music files. Currently only mp3 is supported, with future goals of mp4/m4a and flac. Updates date tag with Release Date from guessing the album's wikipedia page from artist and album tags in file.

To generate the file list you can pass in .m3u playlists (if list only has filepaths, no metadata) or pipe output of `find * | grep ".mp3$"`
