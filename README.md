After some research, watching how others failed to create this, I made the evilest online chess automatic 
player, lulz. This reads the board via screenshot, comparing each square on the image with a previously saved initial board's squares, where the pieces are known, trading info with a running chess engine.
Don't just load stockfish on it, this is dumb. It's meant to test experimental chess engines, know how well they're doing.
       Methods like javascript injection to automate chess playing on websites like chess.com or lichess most likely fail, as the pages admins will know if this kind of stuff is happening, as reported by some who tried.<br>
       This approach seems to be the safest, the downside is that a not perfect screen positioning will screw the entire match. Also, piece position recognition may sometimes fail.
       
       The user needs to prepare his browser window running the web board showing chess starting position (from white point of view), with the browser's zoom and positioning at the way meant to be played by the engine.<br><br>
       * Setup the screen and run '$runGame.py --reference' <br>
       * If there is no game to play just exit the program after few seconds. Or just let it play.
       * Don't move the screen away from the optimal position. Don't zoom. <br>
       * Avoid alt-tabbing from the browser window. This will screw your mouse operations while it runs, so just watch. <br>
       * Start the game, then run the script.<br><br>
       
Requires: [python modules] imagehash, python-chess, pyautogui<br>
	  [executables] imagemagick, xdotool

Usage:
  1- Open the chess board and make the reference screenshot as described. [one-time job]
  2- Set 'WhiteSquareColor' variable @./keyConstants.py. This is the color of the light chess squares on the screenboard, on rgb format like this:
  `WhiteSquareColor = (240,217,181)`
  3- Start the game, run 'runGame.py'.