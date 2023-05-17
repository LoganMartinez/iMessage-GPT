-- usage: osascript sender.scpt [chatId] [isGroupChat] [isImage] [message]

on run argv
	set chatId to item 1 of argv
	set isGroupChat to (item 2 of argv) as integer
  set isImage to (item 3 of argv) as integer
  set mymessage to item 4 of argv

  if isImage = 1 then
    tell application "Finder"
        set current_path to container of (path to me) as alias
        set current_path to POSIX path of current_path
    end tell
    set envFile to current_path & "../.env"
    set picFolder to do shell script "source " & envFile & "; echo $PICTURES_FOLDER"
    set mymessage to POSIX file mymessage
  end if
	
	tell application "Messages"
		set targetService to id of 1st account whose service type = iMessage
		if isGroupChat = 0 then
			set targetBuddy to participant chatId of account id targetService
			send mymessage to targetBuddy
		else
			set theChat to chat id ("iMessage;+;" & chatId) of account id targetService
			send mymessage to theChat
		end if
	end tell
end run