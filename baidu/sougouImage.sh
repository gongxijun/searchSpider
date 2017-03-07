sudo python2.7  sougouImage.py   --dest_dir /data2/xijun.gong/jd_image_data   --stride 10  --config_path profile.txt 1>/data1/xijun.gong/baiduImage/$(date +%y%m%d)_sougouImage.log 2>&1 & $@
