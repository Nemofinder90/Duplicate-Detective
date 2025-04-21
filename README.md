
# Duplicate Detective

Find and remove duplicate files within a chosen folder! This tool compares file *content*, so it finds identical files even if their names are different. It's useful for cleaning up any folder, mainly made for sims 4 mods/cc to clean up the mods a bit.
but of course it can be used for other sutff aswell.

![Screenshot of Duplicate Detective](<https://github.com/Nemofinder90/Duplicate-Detective/blob/main/Screenshot%202025-04-14%20004259.png?raw=true>)


## Features

* Finds **exact duplicate files** based on content (MD5 Hash).
* Scans the single folder you select (including all folders inside it).
* Displays results clearly, grouping duplicates under the first copy found.
* Shows file name, folder path, and size.
* Allows selecting individual duplicates or automatically selecting all duplicates in each group (keeping the first one).
* Permanently deletes selected files after asking for confirmation.
* Includes a progress bar during scanning.
* Offers both Light and Dark mode themes.

## How to Use

1.  **Open the Application:** Find the `duplicate detective` folder (you might have unzipped it). Inside, double-click on `duplicate detective.exe` to start the program.
2.  **Select Folder:** Click the "Select Folder" button in the sidebar on the left. Choose the main folder you want to check for duplicates. The folder path will appear in the sidebar.
3.  **Scan:** Click the "Scan Selected Folder" button. A progress bar will show while the program reads your files. Please wait for it to finish.
4.  **Review Results:** Any duplicate files found will appear in the main list. Each group shows the first found file (top level) and any identical copies nested underneath it.
5.  **Select Files for Deletion:**
    * Click on the duplicate files (the nested ones) you want to remove. Selected files will be highlighted.
    * OR click the "Select Dupes (Keep First)" button (bottom-right) to automatically select all the nested duplicates in the list.
6.  **Delete:** Click the "Delete Selected" button (red button, bottom-right). **Be careful!** The program will ask you to confirm before **permanently deleting** the selected files.
7.  **(Optional) Change Theme:** Use the "Dark Mode" switch in the bottom-left sidebar to toggle between light and dark appearances.


## ❗ Note on Deletion Errors ("Access Denied")

Sometimes, Windows Security might block the program when you try to delete files located in protected folders (like Documents, Pictures, Desktop), showing an "Access Denied" error.

*This is *not* a virus You can downloade the code and look urself*⚠️ It happens because the app is new/unknown to Windows.

**Quick Fix**

1.  Search Windows for "**Controlled folder access**".
2.  Click "**Allow an app through Controlled folder access**".
3.  Click "**Add an allowed app**" -> "**Browse all apps**".
4.  Find and select the `duplicate detective.exe` file.

This should give the app permission to delete files u want in those protected folders.
