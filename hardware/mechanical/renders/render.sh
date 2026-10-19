#!/bin/sh
# Regenerate all PNG renders. Run from this directory after the CAD export.
set -e
R="--projection=o --imgsize=1400,900 --colorscheme=Tomorrow"
openscad -q -o render-assembled.png --camera=0,0,5,60,0,35,230 $R -D 'mode="assembled"' scene.scad
openscad -q -o render-exploded.png  --camera=0,0,8,60,0,35,300 $R -D 'mode="exploded"'  scene.scad
openscad -q -o render-open.png      --camera=0,0,5,0,0,0,160   $R -D 'mode="open"'      scene.scad
openscad -q -o render-tray.png      --camera=0,0,5,0,0,0,160   $R -D 'mode="tray_only"' scene.scad
openscad -q -o render-shell.png     --camera=0,0,0,55,0,25,220 $R -D 'mode="shell"'     scene.scad
openscad -q -o render-lid-under.png --camera=0,0,10,180,0,0,160 $R -D 'mode="lid_under"' scene.scad
openscad -q -o render-usb-end.png   --camera=0,0,5,90,0,90,120 $R -D 'mode="usb_end"'   scene.scad
openscad -q -o render-top.png       --camera=0,0,5,0,0,0,160   $R -D 'mode="assembled"' scene.scad
