# Pixiv Downloader
A simple tool to download images or videos (Ugoira) from [Pixiv](https://www.pixiv.net)



## Requirements to use the scripts:

  - Double-click on _install_requirements.bat_ to install the required dependencies and Python 3.13
  - Download [ffmpeg](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z) and extract the folder "ffmpeg" on the main folder directory.
  
  

## Usage:

1. Double-click on _PixivDownloader.bat_ to launch the downloader. You will see this menu:

<img src="https://files.catbox.moe/pu3e16.png" width="700"/>

   From there you can pick the type of content you can download.

2. The first time you run the downloader you will need to input your PHPSESSID associated to your Pixiv session.


<img src="https://files.catbox.moe/c2u847.png" width="700"/>

   You can get that data logging in your Pixiv account, opening Web Developer Tools on your preferred Web Browser, and going to Storage>Cookies. Open the Cookies associated to pixiv.net and find the PHPSESSID value for your current session.
   
   
<img src="https://files.catbox.moe/lk5139.png" width="700"/>
   

3. After to input your PHPSESSID and selecting what you want to download you will be asked to input the Pixiv URL:


<img src="https://files.catbox.moe/izhcbj.png" width="700"/>


4. Copy and paste the Pixiv URL there and hit Enter, the download will start.
5. After the download is completed you can get the files going to the folder "Pixiv_Downloads".


### NOTE: The PHPSESSID value will expire after a month, so remember to get it again if you can't download stuff anymore.
