# Say It Once

*Easier to read: double-click `START-HERE.html` in this folder to open this guide as a page in your browser.*

You do not need any tech experience. This guide shows every click, in order. Go slowly, tick each step off as you go, and you will have your first content pack today.

## Read this first: Words you will see

Nothing here is hard. These are just the few words this guide uses.

- **Folder:** Like a folder in a filing cabinet. It holds files.
- **Zip file:** A folder squeezed into one file so it is easy to send. You "unzip" it to open it back up.
- **Download:** Saving a file from the internet onto your computer. It usually lands in a folder called **Downloads**.
- **Click:** Press the left button on your mouse (or tap your trackpad) while the arrow is on the thing.
- **Terminal (Mac) and PowerShell (Windows):** A plain window where you type one short instruction and press Enter. You will only use it a few times, and this guide tells you exactly what to type.
- **Enter:** The key on your keyboard that tells the computer "go". On some keyboards it says Return.
- **Paste:** Mac: hold **Command** and press **V**. Windows: hold **Ctrl** and press **V**.

### What you need before you begin

- A **Mac or Windows** laptop or desktop. Chromebooks, tablets and phones can not run Say It Once yet. If you only have a Chromebook, a borrowed Mac or Windows computer will do.
- The internet.
- A **paid Claude plan**. Claude is the helper that does the work. This is the only thing that costs money.
- The **say-it-once.zip** file you were given.
- About 30 minutes, one time. After that, it is a few minutes each time you use it.

> **Stuck? You did not do it wrong.** Take a screenshot of what you see and give it to Claude, and it will help you set it up. Just drop the picture into the chat and say what you were trying to do. (Claude is step 3 in Part 1. Until it is installed, send your screenshot to whoever gave you Say It Once.)

## Part 1, about 15 minutes: Install three free helpers

Chrome, Python and Claude. Do them in this order. A fourth, ffmpeg, is optional.

### 1. Google Chrome

Chrome is a web browser. Say It Once uses it quietly in the background to make your pictures and videos. If you already have Chrome (or Edge or Brave), skip to Python.

1. Open any web browser. Click the long bar at the very top and type **google.com/chrome**. Press Enter.
2. Click the big blue **Download Chrome** button.
3. When it finishes, open the file you downloaded.
4. **Mac:** a small window opens. Drag the Chrome icon onto the Applications folder in that window. **Windows:** it installs by itself. If it asks, click Yes.

> **You should see:** Chrome opens on your screen. That is all. You never need to do anything else with it.

### 2. Python

Python is a quiet helper that runs behind the scenes. You will never use it yourself. Follow the part for your computer.

##### Mac

1. Press **Command + Space** together. A small search bar appears. Type **Terminal** and press Enter. A window with text opens.
2. Type (or paste) this exactly: `python3 --version` and press Enter.
3. If you see **Python 3** followed by numbers, like Python 3.9.6, you are done. Close the window.
4. If a box pops up asking to install "command line developer tools", click **Install**, agree, and wait. It can take several minutes. When it says it is done, do step 2 again.
5. If you see "command not found" instead, go to **python.org/downloads**, click the big yellow **Download Python** button, open the file, and click Continue until it finishes. Then do step 2 again.

##### Windows

1. Open a web browser and go to **python.org/downloads**. Click the big yellow **Download Python** button.
2. Open the file you downloaded.
3. A window opens. **Before you do anything else**, look at the bottom and tick the box that says **Add python.exe to PATH**. This is the one step people miss.
4. Click **Install Now**. Wait until it says it worked, then click **Close**.
5. To check: click the **Start** button, type **PowerShell**, and press Enter. In the window that opens, type `python --version` and press Enter.

> **You should see:** Python 3 followed by numbers, like Python 3.12.1.

### 3. Claude

Claude is the helper you will talk to. You type normal sentences, like texting a friend, and it does the work. You need a paid plan.

##### Easiest way: the Claude app

1. Go to **claude.com/download**. Click the download for your computer (Mac or Windows).
2. Open the file and install it the same way you installed Chrome.
3. Open Claude. Sign in. If you do not have an account yet, make one and choose a paid plan.
4. Look at the top of the Claude window for a tab called **Code**. Click it.

> **You should see:** A tab called Code. If you do not see it, use the other way.

##### Other way: Claude Code

This one is a little more technical. Only use it if the Claude app has no Code tab.

1. Go to **claude.com/claude-code** and follow the install steps for your computer.
2. Windows may ask for a free tool called Git for Windows. That page tells you how to get it.
3. If you get stuck, send a screenshot to whoever gave you Say It Once.

### 4. ffmpeg (optional, for animated videos)

**Skip this for now.** Everything else works without it. Later, if you want the animated carousel videos, tell Claude "help me get ffmpeg" and it will walk you through it. For reference, the one-line installs are below.

##### Mac

`brew install ffmpeg` (needs a free tool called Homebrew first)

##### Windows

`winget install Gyan.FFmpeg`

## Part 2, about 5 minutes: Put Say It Once in the right place

Say It Once is a folder. It needs to live in your home folder, the one with your own name on it.

> **Why not Downloads, Desktop or Documents?** Those folders can be protected or copied to the cloud, which causes confusing errors. Your home folder is safe.

### 1. Find the zip file

##### Mac

1. Click the blue face icon at the bottom of your screen. This is **Finder**.
2. In the list on the left, click **Downloads**.
3. Look for a file called **say-it-once.zip**.

##### Windows

1. Click the yellow folder icon at the bottom of your screen. This is **File Explorer**.
2. In the list on the left, click **Downloads**.
3. Look for a file called **say-it-once** (it may have a zipper on the icon).

### 2. Unzip it

##### Mac

1. **Double-click** say-it-once.zip.

> **You should see:** A new folder called say-it-once appears right next to it.

##### Windows

1. **Right-click** the file (press the right button on your mouse, or tap with two fingers).
2. Click **Extract All**, then click **Extract**.

> **You should see:** A new window opens showing the unzipped folder. Close it. Do not run Say It Once from inside the zip.

### 3. Move the folder to your home folder

##### Mac

1. Keep your Downloads window open. Press **Command + N** to open a second Finder window.
2. In the new window, press **Command + Shift + H**. This opens your home folder, the one with your name on it.
3. Drag the **say-it-once** folder from the Downloads window into the home folder window. To drag, click it, hold the button down, move it, and let go.

##### Windows

1. Keep your Downloads window open. Press the **Windows key + E** to open a second File Explorer window.
2. Click the long bar at the top of the new window, type **%userprofile%** and press Enter. This opens your home folder. It is also called `C:\Users\YourName`.
3. Drag the **say-it-once** folder from the Downloads window into the home folder window. To drag, click it, hold the button down, move it, and let go.

> **You should see:** Your home folder now has a folder called say-it-once. Inside it are folders like brand, engine, inbox and outputs, and a file called START-HERE. If you only see one more folder also called say-it-once, that inner one is the one to move.

## Part 3, about 3 minutes: Open Claude inside that folder

This tells Claude where Say It Once lives.

### If you use the Claude app

1. Open the Claude app and click the **Code** tab at the top.
2. Click the button that lets you choose a folder.
3. Find your home folder, click **say-it-once**, and click the button to open or select it.
4. A box to type in appears near the bottom of the window. That is where you will talk to Claude.

### If you use Claude Code in Terminal or PowerShell

##### Mac

1. Open **Terminal** (Command + Space, type Terminal, Enter).
2. Type `cd ` and then press the space bar once. (That is the letters c and d, then a space.)
3. Drag the **say-it-once** folder into the Terminal window and let go. Its address fills in by itself.
4. Press **Enter**.
5. Type `claude` and press **Enter**.

##### Windows

1. Open the **say-it-once** folder in File Explorer so you can see what is inside it.
2. Click the long address bar at the top, delete what is there, type **powershell** and press **Enter**. A blue window opens.
3. Type `claude` and press **Enter**.

> **You should see:** A box you can type in, and Claude waiting for you. You are in.

Now type this and press Enter:

**Type this and press Enter:** `set me up`

Say it just like you would text it.

## Part 4, about 10 minutes, one time: Tell Claude about you

This is the fun part. Claude learns your business, your people and how you sound.

### What happens

1. Claude asks you a few questions, one or two at a time. Answer in your own words, like you are talking to a friend. There are no wrong answers.
2. Claude may pop up a box asking permission to do something, like run a helper. This is normal. Read the short description and click **Allow** or **Yes**.
3. Next, Claude opens your **Design Studio** in your web browser. Click through the looks and pick the colors and fonts you love. You can change them any time.
4. When it is done, Claude tells you your voice and your design are saved.

> **You should see:** A message from Claude saying you are set up. You only ever do this part once.

> **If Claude says it cannot find Python,** type which one you installed (`python` or `python3`) and press Enter. It will work out the rest.

## Part 5, from now on: Make your first content pack

This is all you ever do from now on.

### 1. Give Claude your material

Your material can be a transcript, a course lesson, a podcast, a voice note, or an article. Pick the easiest way for you:

##### Easiest: paste it

Copy your text, click in Claude's box, **paste it** (Command + V on a Mac, Ctrl + V on Windows), and press Enter.

##### Or: drop in a file

1. Open your **say-it-once** folder.
2. Open the folder called **inbox**.
3. Drag your file in. Text, Word and PDF files all work.

### 2. Say the words

**Type this and press Enter:** `run it`

Type it and press Enter. Claude may ask what you want back. Pick Everything and Standard if you are not sure.

Then wait. A full pack takes a few minutes, and the pictures and videos take the longest. Leave Claude open. You will see it working.

### 3. Open your pack

Claude tells you when it is done and where everything is. These are the three files to open. Double-click any of them and they open in your web browser:

- `outputs` then the folder with today's date, then **00-preview.html** to see all your pictures.
- The same folder, then **content-calendar.html** for what to post each day.
- The same folder, then **00-start-here.md** for your first three days and a short list of things to double-check before you post.

You can also ask Claude: "Put my whole pack on one page." You get one page with every piece, a Copy button on each, and download buttons for your pictures and videos.

## The fun part: Make it look amazing

Your colors, your fonts, your photos.

### 36 carousel layouts

In your colors. Each carousel in a pack gets its own look, and you can change any slide in the carousel editor. Just say "open my carousel editor." When you finish changing things, click **Export** in the editor, then come back to Claude and say **"I am done editing."** That is what updates your content page, your PDF and your videos with your changes. Until you say it, your page still shows the old version.

### Photo backgrounds

Drop your photos in the **brand** folder, inside the **photos** folder, and they go behind your cover, closing and quote slides. No photos? Say **"make me photos."** That needs your own OpenAI or Google Gemini key, and Claude asks before spending anything.

### Animated carousels

Text rises in line by line, photos drift slowly, and slides swipe into each other. Post them as video slides, a Reel or a Story. This needs the free ffmpeg tool from Part 1. Claude tells you if you have it.

## No commands, ever: Things you can say

Plain words work. Type them just like this.

- "Show me designs"
- "Change my colors"
- "Make the reels shorter"
- "Redo carousel 3, punchier"
- "Try a different layout for this one"
- "Add my photos to the carousels"
- "Make the doodles more botanical"
- "Open my carousel editor" (36 layouts, edit in your browser)
- "I am done editing" (Say this after you change things in the editor. It updates your page, PDF and videos.)
- "Update me" (Newest version. Your brand, voice, photos and packs are never touched.)
- "Stop making blog posts" (or "start making LinkedIn")
- "Animate this carousel for a Story"
- "Make me a 60 day calendar starting December 1"
- "Give me talking points for a Live"
- "More threads from this lesson"
- "This does not sound like me" (It asks for an example and learns.)

## Worth a read: Good to know

### It writes from your material

It will not make up stories, numbers or quotes. Anything it was not sure about is listed in the review file. Read that list before you post.

### Scripture

If you teach scripture, it paraphrases with a reference and lists every one for you to check against your own translation.

### You publish

It prepares everything. It never posts for you.

### Your own fonts

Drop your font files in the **brand** folder, inside the **fonts** folder, and name them like `Family-Bold.woff2` or `Family-Italic.ttf`. Then say **"use my font."** The bundled fonts are free open-license fonts.

### Short material, smaller pack

Under about 800 words you get half the usual amount.

### If something looks off

Say what you see, like "the text is cut off on slide 4" or "the calendar skipped Sunday." It will fix it and re-check.

### Coming back another day

Open Claude, open your say-it-once folder the same way as in Part 3, then say **run it** with new material. You never have to do the install steps again.

