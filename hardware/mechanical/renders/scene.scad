// OpenPocket render scene. Usage: ./render.sh (cameras inside)
mode = "assembled";   // assembled | exploded | open | lid_under | shell | tray_only | usb_end
E = "../export/";
module part(f, c) { color(c) import(str(E, f)); }
explode = (mode == "exploded") ? 1 : 0;
AL = [0.80, 0.81, 0.83];
PR = [0.16, 0.16, 0.18];

// aluminium shell + magnets
if (mode != "lid_under") translate([0,0,-explode*16]) { part("openpocket-shell.stl", AL); part("comp-magnets.stl", [0.3,0.3,0.3]); }
// tray + internals
if (mode != "shell" && mode != "lid_under") {
  translate([0,0,-explode*6]) part("openpocket-tray.stl", PR);
  if (mode != "tray_only") translate([0,0,-explode*6]) {
    part("vendor-xiao.stl", [0.1,0.45,0.2]);
    part("comp-battery.stl", [0.75,0.75,0.6]);
    part("comp-sd.stl", [0.15,0.35,0.6]);
    part("comp-switch.stl", [0.9,0.2,0.2]);
    part("openpocket-button-cap.stl", [0.95,0.45,0.1]);
  }
}
// lid group
if (mode == "assembled" || mode == "exploded" || mode == "lid_under") {
  translate([0,0,explode*14]) {
    part("openpocket-lid.stl", AL);
    part("openpocket-rf-insert.stl", PR);
    part("vendor-mic1.stl", [0.1,0.1,0.6]); part("vendor-mic2.stl", [0.1,0.1,0.6]);
    part("comp-led.stl", [0.9,0.5,0.1]); part("comp-motor.stl", [0.5,0.5,0.5]); part("comp-antenna.stl", [0.9,0.8,0.2]);
    translate([0,0,explode*6]) part("comp-screws.stl", [0.6,0.6,0.65]);
  }
}
if (mode == "open") { part("vendor-mic1.stl", [0.1,0.1,0.6]); part("vendor-mic2.stl", [0.1,0.1,0.6]); part("comp-led.stl", [0.9,0.5,0.1]); part("comp-motor.stl", [0.5,0.5,0.5]); part("comp-antenna.stl", [0.9,0.8,0.2]); }
