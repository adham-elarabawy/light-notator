# light-notator
A custom frame annotator implemented with p5 and python.
--------------------------------------------------------

# Installation:
1) Clone this repository. It doesn't really matter where you clone it to, it is a standalone folder.
2) Enter the command line (it doesn't matter what system you are on, windows/linux/mac). Navigate to the directory that you cloned this repository to. Run the following command:
`pip install -r requirements.txt`

All the python dependencies should be installed after the command above finished installing. 

3) The last preqrequisite is GLFW. Internally p5(one of the python libraries) uses GLFW to handle window events and to work with OpenGL graphics. Follow the below instructions to install GLFW based on which system you are on.

Windows: 
--------
First, download and install the pre-compiled Windows binaries from the official GLFW downloads page (https://www.glfw.org/download.html). During the installation process, make sure to take note of the downloaded folder which stores the GLFW binaries.

Finally, the GLFW installation directory should be added to the system path. Make sure to add containing the .dll and .a files (for example: \<path to glfw>\glfw-(version_number).bin.WIN64\lib-mingw-w64)

First locate the “Environment Variables” settings dialog box. On recent versions of Windows (Windows 8 and later), go to System info > Advanced Settings > Environment Variables. On older versions (Windows 7 and below) first right click the computer icon (from the desktop or start menu) and then go to Properties > Advanced System Settings > Advanced > Environment Variables. Now, find and highlight the “Path” variable and click the edit button. Here, add the GLFW installation directory to the end of the list and save the settings.

MacOS, Linux:
-------------
Most package systems such as homebrew, aptitude, etc already have the required GLFW binaries. For instance, to install GLFW on Mac using homebrew, run

`brew install glfw`

Similarly, on Debain (and it’s derivatives like Ubuntu and Linux Mint, run: 

`sudo apt-get install libglfw3`

For other Linux based systems, find and install the GLFW package using the respective package system.

# To Run/Use
1) Place your images in the local `input/` directory.
2) Run the python script (either by double-clicking the python file, or by running the python script through the command line)
3) Click three points on the corners of what you are trying to annotate, and the annotator will fit a rotated bounding box (rotated rectangle) to those points.
4) When you're done annotating, you can close the annotator. All of your annotations will be in the input directory with the same name as their respective frames, but in CSV format. 

# Annotation Format
All of the annotations are done with relative format:
(x coordinate of center of bounding box / width of screen), (y coordinate of center of bounding box / height of screen), (width bounding box / width of screen), (height of bounding box / height of screen), (angle of rotated bounding box)

