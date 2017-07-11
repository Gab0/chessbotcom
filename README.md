After some research, watching how others failed to create this, I made the evilest online chess automatic 
player, lulz. This reads the browser board via screenshot, periodically, comparing each square on the image with a previously saved initial board's squares, where the pieces are known. Then trades info with a running chess engine.
Don't just load stockfish on it, this is dumb. It's meant to test experimental chess engines, know how well they're doing.
       Methods like javascript injection to automate chess playing on websites like chess.com or lichess most likely fail, as the page admins will know if this kind of stuff is happening, as reported by some who tried.<br>
       A safe approach... the downside is that a non perfect screen positioning will screw the rest of the match. Also piece position recognition may fail.. game lost.
       
       
Requires: [python modules] imagehash, python-chess, pyautogui<br>
	  [executables] imagemagick, xdotool

Usage:<br>
    -> Open the online chess website, showing the board on the starting position (white bottom).<br/>
    -> Set 'WhiteSquareColor' variable @./keyConstants.py. Corresponds to the color of white chess squares on the screenboard. <br/>
    RGB tuple values:        'WhiteSquareColor = (240,217,181)'<br/>
    -> Setup the screen and run '$./runGame.py --reference' (@ first run, redo whenever you change screen positioning/configs for whatever reason.)<br/>
    -> Start the game, quickly run '$./runGame.py'<br/>
    -> Don't move the screen away from the referenced position, don't zoom.<br/>
    -> Game window needs to be on foreground. Clicking has to be done.<br/>
    -> Avoid alt-tabbing from the browser window. This will screw your mouse operations while it runs, so just watch.<br/>
