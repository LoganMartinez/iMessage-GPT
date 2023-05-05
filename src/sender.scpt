

on run argv
  set envFile to item 1 of argv & "/../.env"
  set chatId to do shell script "source " & envFile & "; echo $CHAT_ID"

  tell application "Messages"
    set mymessage to item 2 of argv
    set targetService to id of 1st account whose service type = iMessage
    set theChat to chat id ("iMessage;+;" & chatId) of account id targetService
    -- log mymessage
    send mymessage to theChat
  end tell
end run