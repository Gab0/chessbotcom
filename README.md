After some research, watching how others failed to create this, I made the most evil online chess automatic 
player, lulz. This reads the board via screenshot, comparing each square on the image with a previously saved initial board's squares, where the pieces are known, trading info with a running chess engine.
Don't just load stockfish on it, this is dumb. It's meant to test experimental chess engines to get some feedback.
       Methods like javascript injection to automate chess playing on websites like chess.com or lichess most likely fail, as the pages admins will know if this kind of stuff is happening, as reported by some who tried.<br>
       This approach seems to be the safest, the downside is that a not perfect screen positioning will screw the entire match. Also, piece position recognition may sometimes fail.
       The user needs to take a screenshot of his browser window running the web board showing chess start position from white point of view), with the browser's zoom and positioning at the way this script will be used with.<br><br>
       * Don't move the screen away from the optimal position. Don't zoom. <br>
       * Avoid alt-tabbing from the browser window. This will screw your mouse operations while it runs, so just watch. <br>
       * Start the game, then run the script.<br><br>
       
Requires: [python modules] imagehash, python-chess, pyautogui<br>
	  [executables] shutter, xdotool
