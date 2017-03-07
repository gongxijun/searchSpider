sudo python2.7  baiduImage.py   --dest_dir /data2/xijun.gong/jd_image_data   --stride 10  --config_path profile.txt 1>/data1/xijun.gong/baiduImage/$(date +%y%m%d)_baiduImage.log 2>&1 & $@
