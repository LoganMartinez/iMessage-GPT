

on run argv
  set envFile to item 1 of argv & "/../.env"
  set chatId to do shell script "source " & envFile & "; echo $CHAT_ID"

  tell application "Messages"
    set replyId to item 2 of argv 
    set mymessage to item 3 of argv
    set targetService to id of 1st account whose service type = iMessage
    set theChat to chat id ("iMessage;+;" & chatId) of account id targetService
    -- set replyMessage to message id replyId of theChat
    -- log replyMessage
    -- reply mymessage to replyMessage
  end tell
end run