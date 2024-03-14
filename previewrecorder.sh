libcamera-vid -o test.h264 -t 30000 --width 1280 --height 720 --framerate 60 --codec h264 --profile high --quality 100 --intra 5 --autofocus-mode continuous --autofocus-range full --autofocus-speed fast
ffmpeg -framerate 60 -y -i test.h264 -c copy test.mp4
rm test.h264
echo "Saved as test.mp4"