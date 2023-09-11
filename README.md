![Captura_de_Tela__16_-removebg-preview](https://github.com/pedrohusky/Youber/assets/59580251/fb118f4d-84f6-44f6-9367-28e5b42d7646)
# Youber - YouTube Downloader with a Modern UI

Youber is a Python-based YouTube downloader with a modern user interface. It provides the convenience of downloading multiple videos in a row (playlist links) or a single video link. Youber is designed to be simple yet powerful, offering features that make video downloading and conversion a breeze.

## Why Youber?

Youber was created to provide a YouTube downloading solution that doesn't rely on third-party downloaders. It's a simple yet powerful tool that puts you in control of your video downloads and conversions.

Ah, the name origin: You<sub>tu</sub>b<sub>eDownload</sub>er -> **Youber**


## Features

- **Modern UI:** Built using customTkinter to provide an intuitive and modern user interface.
-  *Video UI*
-   ![Captura de Tela (14)](https://github.com/pedrohusky/Youber/assets/59580251/a698f2aa-d344-49f6-876f-cc311b93873c)
-  *Playlist UI*
-   ![Captura de Tela (13)](https://github.com/pedrohusky/Youber/assets/59580251/68aca763-dd0b-4a95-baaf-3a7d6f546400)

- **Output Format Selection:** You can easily choose the output format for your downloaded videos, making it conversion-compatible.
  ![Captura de Tela (15)](https://github.com/pedrohusky/Youber/assets/59580251/94219545-1ae2-456b-bc4b-cc210ebd104f)

- **Quality Selection:** For single video downloads, Youber allows you to select the desired quality.

- **Metadata Inclusion:** When converting videos to MP3, metadata is automatically included like artist, album cover, year (the year being the video published date).

- **Playlist Downloads:** Youber supports downloading entire playlists, giving you the choice to download either the video or audio.

## How to Use

To use Youber, follow these steps:

1. First of all, install requirements: 
- ```
  pip install requirements.txt
  ```

2. Run Youber using Python:
- ```bash
  python main.py
  ```

3. Alternatively, you can execute the pre-built executable located in the `/dist/` directory.

4. If you prefer, create your own executable using the `create_exe.py` file by running:
- ```bash
  python create_exe.py
  ```



## To-Do List

- Add quality selection for playlist downloads.
- Implement a search function to search YouTube playlists and videos with keywords, effectively turning Youber into a YouTube search and downloader.

Feel free to contribute and help improve Youber!

## License

This project is licensed under the [MIT License](LICENSE).


