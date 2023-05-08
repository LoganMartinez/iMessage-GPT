-- usage: osascript sender.scpt [chatId] [isGroupChat] [message]

on run argv
	set chatId to item 1 of argv
	set isGroupChat to (item 2 of argv) as integer
	set mymessage to item 3 of argv
	
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