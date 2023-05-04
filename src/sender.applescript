set envFile to "../.env"

set chatId to do shell script "source " & envFile & "; echo $CHAT_ID"

tell application "Messages"
  set mymessage to "This is Shitnuts speaking, you can disregard this message :)"
  set targetService to id of 1st account whose service type = iMessage
  set theChat to chat id ("iMessage;+;" & chatId) of account id targetService
  send mymessage to theChat
end tell