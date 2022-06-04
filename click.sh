#!/bin/sh
# used commands

#which finds the location of the program

#TODO:
#https://www.youtube.com/watch?v=CGZEsyoyIqc&ab_channel=NovaspiritTech
#https://www.youtube.com/watch?v=7p3hvtYUnTI&ab_channel=NovaspiritTech
#Link how to set up screen share: https://www.youtube.com/watch?v=HAJaNuFIvnU

xprop_command=`which xprop` #class of window
xdotool_command=`which xdotool` #active window
xte_command=`which xte` #mimic of mouse click

#resolution is: 1360x768

while :
do
	# -n means if string is not empty

    if [ -n "$xprop_command" -a -n "$xdotool_command" -a -n "$xte_command" ]; then
      # get active window id
      active_window_id=`$xdotool_command getactivewindow`
      # get class of the active window
      window_class=`$xprop_command -id $active_window_id | sed -n -e "s/^WM_CLASS(STRING).*\"\(.*\)\", \".*\"/\1/ p"`
      # execute only when active windows is Google Chrome
      if [ "$window_class" = "scrcpy" ]; then
          #delete current data
          $xte_command "mousemove 1050 850"
          sleep 1
          $xte_command 'mouseclick 1'
          sleep 1
          $xte_command "mousemove 1050 600"
          sleep 1
          $xte_command 'mouseclick 1'
          echo "Yes sir"
          #wait X seconds to collect new data
          #$xte_command "sleep $1"

          #coordinates for save button: 740 120
          #$xte_command "mousemove 1050 180"
          #$xte_command "mouseclick 1"

          break
      fi
    fi
done
